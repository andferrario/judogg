from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from judogg.app.domain.categories import sort_orders
from judogg.app.domain.model import Athlete, Catalogue, Filters, ScoreRow, Tag, Thresholds
from judogg.app.domain.numbers import Sample, athlete_sample, ratio, round4
from judogg.app.domain.profiles import AthleteProfile, athlete_profiles
from judogg.app.domain.refs import TechniqueRef, WeightRef, technique_ref, weight_ref

MAX_PAIRS = 20


@dataclass(frozen=True)
class Cohort:
    eligible: int
    with_technique: int
    sample: Sample


@dataclass(frozen=True)
class Companion:
    technique: TechniqueRef
    n_both: int
    p_given: float | None
    p_base: float | None
    lift: float | None
    sample: Sample


@dataclass(frozen=True)
class PairAthlete:
    athlete: Athlete
    weight: WeightRef
    n_technique: int
    n_with: int
    n_total: int


@dataclass(frozen=True)
class PairAthletes:
    technique: TechniqueRef
    rows: tuple[PairAthlete, ...]


@dataclass(frozen=True)
class Repertoire:
    technique: TechniqueRef
    cohort: Cohort
    companions: tuple[Companion, ...]
    pair_athletes: PairAthletes | None


@dataclass(frozen=True)
class Pair:
    a: TechniqueRef
    b: TechniqueRef
    n_both: int
    support: float | None
    confidence: float | None
    lift: float | None
    sample: Sample


@dataclass(frozen=True)
class MatrixCell:
    n_both: int
    lift: float | None
    sample: Sample


@dataclass(frozen=True)
class Matrix:
    techniques: tuple[TechniqueRef, ...]
    cells: tuple[tuple[MatrixCell | None, ...], ...]


@dataclass(frozen=True)
class RepertoirePairs:
    eligible: int
    sample: Sample
    pairs: tuple[Pair, ...]
    matrix: Matrix


class _Cohort:
    """Eligible athletes and the techniques in their repertoire."""

    def __init__(self, scores: Sequence[ScoreRow], filters: Filters, catalogue: Catalogue) -> None:
        profiles = athlete_profiles(scores, catalogue.tags, sort_orders(catalogue.weights))
        self.min_scores = filters.min_scores_technique
        self.eligible = [p for p in profiles.values() if p.total >= filters.min_scores_athlete]
        self.per_weight = Counter(p.weight for p in self.eligible)
        self.frequency: Counter[int] = Counter()
        self.frequency_per_weight: dict[int, Counter[str]] = {}
        for profile in self.eligible:
            for tag_id in profile.techniques:
                if self.has(profile, tag_id):
                    self.frequency[tag_id] += 1
                    self.frequency_per_weight.setdefault(tag_id, Counter())[profile.weight] += 1

    def has(self, profile: AthleteProfile, tag_id: int) -> bool:
        return profile.techniques[tag_id] >= self.min_scores

    def both(self, first: int, second: int) -> int:
        return sum(1 for p in self.eligible if self.has(p, first) and self.has(p, second))

    def expected_both(self, first: int, second: int) -> float:
        """Athletes expected with both techniques if they were independent within each category."""
        a, b = self.frequency_per_weight[first], self.frequency_per_weight[second]
        return sum(a[w] * b[w] / n for w, n in self.per_weight.items())


def build_repertoire(
    technique: Tag,
    companion: Tag | None,
    scores: Sequence[ScoreRow],
    filters: Filters,
    catalogue: Catalogue,
    athletes: Mapping[int, Athlete],
    thresholds: Thresholds,
) -> Repertoire:
    cohort = _Cohort(scores, filters, catalogue)
    with_x = [p for p in cohort.eligible if cohort.has(p, technique.id)]
    with_x_per_weight = Counter(p.weight for p in with_x)
    companions = []
    for tag_id in cohort.frequency:
        if tag_id == technique.id:
            continue
        both = sum(1 for p in with_x if cohort.has(p, tag_id))
        if not both:
            continue
        with_y_per_weight = cohort.frequency_per_weight[tag_id]
        p_given = both / len(with_x)
        p_base = sum(
            a / len(with_x) * with_y_per_weight[w] / cohort.per_weight[w] for w, a in with_x_per_weight.items()
        )
        companions.append(
            Companion(
                technique_ref(catalogue.tags[tag_id]),
                both,
                round4(p_given),
                round4(p_base),
                round4(p_given / p_base) if p_base else None,
                athlete_sample(both, thresholds),
            )
        )
    companions.sort(key=lambda c: c.technique.name)
    companions.sort(key=lambda c: c.lift or 0.0, reverse=True)
    companions.sort(key=lambda c: c.n_both, reverse=True)
    return Repertoire(
        technique=technique_ref(technique),
        cohort=Cohort(len(cohort.eligible), len(with_x), athlete_sample(len(with_x), thresholds)),
        companions=tuple(companions),
        pair_athletes=_pair_athletes(technique, companion, with_x, cohort, catalogue, athletes),
    )


def _pair_athletes(
    technique: Tag,
    companion: Tag | None,
    with_x: Sequence[AthleteProfile],
    cohort: _Cohort,
    catalogue: Catalogue,
    athletes: Mapping[int, Athlete],
) -> PairAthletes | None:
    if companion is None:
        return None
    categories = {w.code: w for w in catalogue.weights}
    both = [p for p in with_x if cohort.has(p, companion.id)]
    both.sort(key=lambda p: (-(p.techniques[technique.id] + p.techniques[companion.id]), p.id))
    rows = tuple(
        PairAthlete(
            athletes[p.id],
            weight_ref(categories[p.weight]),
            p.techniques[technique.id],
            p.techniques[companion.id],
            p.total,
        )
        for p in both
    )
    return PairAthletes(technique_ref(companion), rows)


def build_pairs(
    scores: Sequence[ScoreRow], filters: Filters, catalogue: Catalogue, top: int, thresholds: Thresholds
) -> RepertoirePairs:
    cohort = _Cohort(scores, filters, catalogue)
    tags = catalogue.tags
    ids = list(cohort.frequency)
    eligible = len(cohort.eligible)
    pairs = []
    for index, first in enumerate(ids):
        for second in ids[index + 1 :]:
            n = cohort.both(first, second)
            if n < thresholds.athlete_sample_small:
                continue
            rarer = cohort.frequency[first] < cohort.frequency[second] or (
                cohort.frequency[first] == cohort.frequency[second] and tags[first].code < tags[second].code
            )
            a, b = (first, second) if rarer else (second, first)
            expected = cohort.expected_both(first, second)
            pairs.append(
                Pair(
                    technique_ref(tags[a]),
                    technique_ref(tags[b]),
                    n,
                    ratio(n, eligible),
                    ratio(n, cohort.frequency[a]),
                    round4(n / expected) if expected else None,
                    athlete_sample(n, thresholds),
                )
            )
    pairs.sort(key=lambda p: (p.a.name, p.b.name))
    pairs.sort(key=lambda p: p.n_both, reverse=True)
    pairs.sort(key=lambda p: p.lift or 0.0, reverse=True)
    chosen = sorted(ids, key=lambda t: (-cohort.frequency[t], tags[t].code))[:top]
    cells = tuple(tuple(_cell(cohort, i, j, thresholds) for j in chosen) for i in chosen)
    return RepertoirePairs(
        eligible=eligible,
        sample=athlete_sample(eligible, thresholds),
        pairs=tuple(pairs[:MAX_PAIRS]),
        matrix=Matrix(tuple(technique_ref(tags[t]) for t in chosen), cells),
    )


def _cell(cohort: _Cohort, first: int, second: int, thresholds: Thresholds) -> MatrixCell | None:
    if first == second:
        return None
    n = cohort.both(first, second)
    expected = cohort.expected_both(first, second)
    return MatrixCell(n, round4(n / expected) if expected else None, athlete_sample(n, thresholds))
