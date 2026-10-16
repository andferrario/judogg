from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from judogg.app.domain.baseline import category_shares, expected_share
from judogg.app.domain.categories import most_frequent_weight, selected_weights, sort_orders
from judogg.app.domain.links import athlete_url
from judogg.app.domain.model import Athlete, Catalogue, CountBy, Direction, Filters, ScoreRow, Tag, Thresholds
from judogg.app.domain.numbers import Sample, count_sample, ratio, round4
from judogg.app.domain.profiles import athlete_profiles
from judogg.app.domain.refs import TechniqueRef, WeightRef, technique_ref, weight_ref
from judogg.app.domain.scores import (
    SideCounts,
    TimingBin,
    ValueShares,
    distinct,
    side_counts,
    technique_groups,
    timing,
)

TOP_ATHLETES = 10
TOP_COUNTRIES = 10


@dataclass(frozen=True)
class TechniqueKpis:
    n_scores: int
    rank: int | None
    of: int
    pct: ValueShares
    overall_pct_ippon: float | None
    right_share: float | None
    unknown_side_share: float | None
    n_athletes: int
    n_awasete: int
    gs_share: float | None
    overall_gs_share: float | None


@dataclass(frozen=True)
class WeightShare:
    weight: WeightRef
    n: int
    total: int
    share: float | None
    side: SideCounts
    sample: Sample


@dataclass(frozen=True)
class TrendPoint:
    year: int
    n: int
    total: int
    share: float | None


@dataclass(frozen=True)
class Trend:
    points: tuple[TrendPoint, ...]
    ruleset_changes: tuple[int, ...]
    sample: Sample


@dataclass(frozen=True)
class TopAthlete:
    athlete: Athlete
    weight: WeightRef
    n: int
    n_ippon: int
    total_scores: int
    share_of_total: float | None
    side: SideCounts
    judobase_url: str


@dataclass(frozen=True)
class CountryLift:
    country_code: str
    total: int
    n: int
    share: float | None
    lift: float | None
    sample: Sample


@dataclass(frozen=True)
class Countries:
    rows: tuple[CountryLift, ...]
    min_scores_country: int


@dataclass(frozen=True)
class TechniqueDetail:
    technique: TechniqueRef
    kpis: TechniqueKpis
    sample: Sample
    by_weight: tuple[WeightShare, ...]
    timing: tuple[TimingBin, ...]
    trend: Trend
    top_athletes: tuple[TopAthlete, ...]
    countries: Countries


@dataclass
class _Scorer:
    id: int
    n: int = 0
    ippon: int = 0
    sides: Counter[Direction] = field(default_factory=Counter)
    weights: Counter[str] = field(default_factory=Counter)


@dataclass
class _Country:
    code: str
    total: int = 0
    n: int = 0
    weights: Counter[str] = field(default_factory=Counter)


def build_technique_detail(
    tag: Tag,
    scores: Sequence[ScoreRow],
    filters: Filters,
    catalogue: Catalogue,
    athletes: Mapping[int, Athlete],
    thresholds: Thresholds,
) -> TechniqueDetail:
    unique = distinct(scores)
    mine = [s for s in scores if s.technique_tag_id == tag.id]
    n = len(mine)
    known_side = [s for s in mine if s.direction != "unknown"]
    values = Counter(s.score_value for s in mine)
    scorers = _scorers(mine)
    rank, of = _rank(tag.id, scores, filters.count_by)
    kpis = TechniqueKpis(
        n_scores=n,
        rank=rank,
        of=of,
        pct=ValueShares(ratio(values["ippon"], n), ratio(values["waza_ari"], n), ratio(values["yuko"], n)),
        overall_pct_ippon=ratio(sum(1 for s in unique if s.score_value == "ippon"), len(unique)),
        right_share=ratio(sum(1 for s in known_side if s.direction == "right"), len(known_side)),
        unknown_side_share=ratio(n - len(known_side), n),
        n_athletes=len(scorers),
        n_awasete=sum(1 for s in mine if s.is_awasete),
        gs_share=ratio(sum(1 for s in mine if s.is_gs), n),
        overall_gs_share=ratio(sum(1 for s in unique if s.is_gs), len(unique)),
    )
    return TechniqueDetail(
        technique=technique_ref(tag),
        kpis=kpis,
        sample=count_sample(n, thresholds),
        by_weight=_by_weight(mine, unique, filters, catalogue, thresholds),
        timing=timing(mine),
        trend=_trend(mine, unique, catalogue, thresholds),
        top_athletes=_top_athletes(scorers, scores, catalogue, athletes),
        countries=_countries(tag, mine, scores, thresholds),
    )


def _scorers(mine: Sequence[ScoreRow]) -> dict[int, _Scorer]:
    scorers: dict[int, _Scorer] = {}
    for score in mine:
        scorer = scorers.get(score.athlete_id)
        if scorer is None:
            scorer = scorers[score.athlete_id] = _Scorer(score.athlete_id)
        scorer.n += 1
        scorer.ippon += score.score_value == "ippon"
        scorer.sides[score.direction] += 1
        scorer.weights[score.weight] += 1
    return scorers


def _rank(tag_id: int, scores: Sequence[ScoreRow], count_by: CountBy) -> tuple[int | None, int]:
    known = [g for g in technique_groups(scores).values() if g.tag_id is not None]
    known.sort(key=lambda g: (g.n if count_by == "event" else len(g.athletes), g.n), reverse=True)
    position = next((index for index, g in enumerate(known, start=1) if g.tag_id == tag_id), None)
    return position, len(known)


def _by_weight(
    mine: Sequence[ScoreRow],
    unique: Sequence[ScoreRow],
    filters: Filters,
    catalogue: Catalogue,
    thresholds: Thresholds,
) -> tuple[WeightShare, ...]:
    totals = Counter(s.weight for s in unique)
    rows = []
    for category in selected_weights(filters, catalogue.weights):
        in_weight = [s for s in mine if s.weight == category.code]
        total = totals[category.code]
        rows.append(
            WeightShare(
                weight_ref(category),
                len(in_weight),
                total,
                ratio(len(in_weight), total),
                side_counts(in_weight),
                count_sample(len(in_weight), thresholds),
            )
        )
    return tuple(rows)


def _trend(mine: Sequence[ScoreRow], unique: Sequence[ScoreRow], catalogue: Catalogue, thresholds: Thresholds) -> Trend:
    totals = Counter(s.year for s in unique)
    counts = Counter(s.year for s in mine)
    years = sorted(totals)
    points = tuple(TrendPoint(y, counts[y], totals[y], ratio(counts[y], totals[y])) for y in years)
    changes = tuple(sorted(r.year_from for r in catalogue.rulesets if years and years[0] < r.year_from <= years[-1]))
    status = count_sample(len(mine), thresholds).status if len(points) >= 3 else "insufficient"
    return Trend(points, changes, Sample(status, len(points), "years"))


def _top_athletes(
    scorers: Mapping[int, _Scorer],
    scores: Sequence[ScoreRow],
    catalogue: Catalogue,
    athletes: Mapping[int, Athlete],
) -> tuple[TopAthlete, ...]:
    order = sort_orders(catalogue.weights)
    categories = {w.code: w for w in catalogue.weights}
    profiles = athlete_profiles(scores, catalogue.tags, order)
    ranked = sorted(scorers.values(), key=lambda a: (-a.n, -a.ippon, a.id))[:TOP_ATHLETES]
    return tuple(
        TopAthlete(
            athlete=athletes[a.id],
            weight=weight_ref(categories[most_frequent_weight(a.weights, order)]),
            n=a.n,
            n_ippon=a.ippon,
            total_scores=profiles[a.id].total,
            share_of_total=ratio(a.n, profiles[a.id].total),
            side=SideCounts(a.sides["left"], a.sides["right"], a.sides["unknown"]),
            judobase_url=athlete_url(a.id),
        )
        for a in ranked
    )


def _countries(tag: Tag, mine: Sequence[ScoreRow], scores: Sequence[ScoreRow], thresholds: Thresholds) -> Countries:
    shares = category_shares(scores)
    countries: dict[str, _Country] = {}
    for score in distinct(scores):
        country = countries.get(score.athlete_country)
        if country is None:
            country = countries[score.athlete_country] = _Country(score.athlete_country)
        country.total += 1
        country.weights[score.weight] += 1
    for score in distinct(mine):
        countries[score.athlete_country].n += 1
    rows = []
    for c in countries.values():
        if c.total < thresholds.min_scores_country:
            continue
        expected = expected_share(shares, c.weights, c.total, tag.id)
        lift = round4((c.n / c.total) / expected) if expected else None
        rows.append(CountryLift(c.code, c.total, c.n, ratio(c.n, c.total), lift, count_sample(c.n, thresholds)))
    rows.sort(key=lambda r: r.country_code)
    rows.sort(key=lambda r: r.n, reverse=True)
    rows.sort(key=lambda r: r.lift or 0.0, reverse=True)
    return Countries(tuple(rows[:TOP_COUNTRIES]), thresholds.min_scores_country)
