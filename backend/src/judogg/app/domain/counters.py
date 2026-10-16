from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from judogg.app.domain.baseline import category_shares, expected_share
from judogg.app.domain.categories import sort_orders
from judogg.app.domain.model import Athlete, Catalogue, Filters, ScoreRow, Tag, Thresholds
from judogg.app.domain.numbers import Sample, athlete_sample, count_sample, round4
from judogg.app.domain.profiles import athlete_profiles
from judogg.app.domain.refs import TechniqueRef, WeightRef, technique_ref, weight_ref
from judogg.app.domain.scores import distinct, technique_groups


@dataclass(frozen=True)
class Specialist:
    athlete: Athlete
    weight: WeightRef
    share: float | None
    n_total: int


@dataclass(frozen=True)
class Specialists:
    n: int
    sample: Sample
    share_threshold: float
    athletes: tuple[Specialist, ...]


@dataclass(frozen=True)
class Conceded:
    n: int
    sample: Sample


@dataclass(frozen=True)
class CounterRow:
    technique: TechniqueRef | None
    n: int
    share: float | None
    base_share: float | None
    lift: float | None
    sample: Sample


@dataclass(frozen=True)
class Counters:
    technique: TechniqueRef
    specialists: Specialists
    conceded: Conceded
    rows: tuple[CounterRow, ...]


def build_counters(
    technique: Tag,
    scores: Sequence[ScoreRow],
    filters: Filters,
    catalogue: Catalogue,
    athletes: Mapping[int, Athlete],
    thresholds: Thresholds,
) -> Counters:
    profiles = athlete_profiles(scores, catalogue.tags, sort_orders(catalogue.weights))
    specialists = [
        p
        for p in profiles.values()
        if p.total >= filters.min_scores_athlete
        and p.main == technique.id
        and p.techniques[technique.id] / p.total >= thresholds.specialist_share
    ]
    specialists.sort(key=lambda p: (-p.techniques[technique.id] / p.total, p.id))
    ids = {p.id for p in specialists}
    conceded = [s for s in scores if s.opponent_id in ids]
    conceded_unique = distinct(conceded)
    shares = category_shares(scores)
    conceded_weights = Counter(s.weight for s in conceded_unique)
    rows = []
    for group in technique_groups(conceded).values():
        share = group.n / len(conceded_unique)
        base = expected_share(shares, conceded_weights, len(conceded_unique), group.tag_id)
        rows.append(
            CounterRow(
                technique=technique_ref(catalogue.tags[group.tag_id]) if group.tag_id is not None else None,
                n=group.n,
                share=round4(share),
                base_share=round4(base),
                lift=round4(share / base) if base else None,
                sample=count_sample(group.n, thresholds),
            )
        )
    rows.sort(key=lambda r: r.technique.name if r.technique else "")
    rows.sort(key=lambda r: r.lift or 0.0, reverse=True)
    rows.sort(key=lambda r: r.n, reverse=True)
    rows.sort(key=lambda r: r.technique is None)
    categories = {w.code: w for w in catalogue.weights}
    return Counters(
        technique=technique_ref(technique),
        specialists=Specialists(
            n=len(specialists),
            sample=athlete_sample(len(specialists), thresholds),
            share_threshold=thresholds.specialist_share,
            athletes=tuple(
                Specialist(
                    athletes[p.id],
                    weight_ref(categories[p.weight]),
                    round4(p.techniques[technique.id] / p.total),
                    p.total,
                )
                for p in specialists
            ),
        ),
        conceded=Conceded(len(conceded_unique), count_sample(len(conceded_unique), thresholds)),
        rows=tuple(rows),
    )
