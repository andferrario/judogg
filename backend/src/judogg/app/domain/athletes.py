import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal, TypedDict

from judogg.app.domain.categories import most_frequent_weight, sort_orders
from judogg.app.domain.envelope import WarningItem
from judogg.app.domain.links import athlete_url
from judogg.app.domain.model import Athlete, Catalogue, ContestRow, ScoreRow, Thresholds
from judogg.app.domain.numbers import Sample, count_sample, ratio, round4
from judogg.app.domain.profiles import main_technique
from judogg.app.domain.refs import TechniqueRef, WeightRef, technique_ref, weight_ref
from judogg.app.domain.score_list import AthleteScoreRow, athlete_score_row, newest_first
from judogg.app.domain.scores import SideCounts, ValueCounts, ValueShares, distinct, technique_groups

SimilarScope = Literal["weight", "all"]
SIMILAR_SCOPES: tuple[SimilarScope, ...] = ("weight", "all")
MAX_SIMILAR = 6
TOP_TECHNIQUES = 3

YearSpan = TypedDict("YearSpan", {"from": int, "to": int})


@dataclass(frozen=True)
class SearchRow:
    athlete: Athlete
    weights: tuple[WeightRef, ...]
    n_scores: int


@dataclass(frozen=True)
class AthleteSearch:
    rows: tuple[SearchRow, ...]


@dataclass(frozen=True)
class AthleteWeight:
    weight: WeightRef
    contests: int


@dataclass(frozen=True)
class AthleteKpis:
    competitions: int
    contests: int
    scores: int
    techniques: int
    ippon_share: float | None
    main_technique: TechniqueRef | None


@dataclass(frozen=True)
class AthleteTechnique:
    technique: TechniqueRef | None
    n: int
    share_of_total: float | None
    counts: ValueCounts
    pct: ValueShares
    n_awasete: int
    side: SideCounts


@dataclass(frozen=True)
class ScoreGroup:
    technique: TechniqueRef | None
    n: int
    rows: tuple[AthleteScoreRow, ...]


@dataclass(frozen=True)
class TopTechnique:
    code: str
    name: str
    group_label: str | None
    domain: Literal["standing", "ground"] | None
    n: int


@dataclass(frozen=True)
class SimilarAthlete:
    athlete: Athlete
    weight: WeightRef
    similarity: float | None
    n_scores: int
    top_techniques: tuple[TopTechnique, ...]
    sample: Sample


@dataclass(frozen=True)
class Similar:
    scope: SimilarScope
    weight: WeightRef
    min_scores_athlete: int
    sample: Sample
    rows: tuple[SimilarAthlete, ...]


@dataclass(frozen=True)
class AthleteDetail:
    athlete: Athlete
    judobase_url: str
    weights: tuple[AthleteWeight, ...]
    years: YearSpan
    kpis: AthleteKpis
    sample: Sample
    techniques: tuple[AthleteTechnique, ...]
    score_groups: tuple[ScoreGroup, ...]
    similar: Similar


@dataclass(frozen=True)
class AthleteResponse:
    warnings: tuple[WarningItem, ...]
    data: AthleteDetail


def _contest_weights(contests: Sequence[ContestRow]) -> dict[int, Counter[str]]:
    weights: dict[int, Counter[str]] = {}
    for c in contests:
        for athlete_id in (c.white_athlete_id, c.blue_athlete_id):
            weights.setdefault(athlete_id, Counter())[c.weight] += 1
    return weights


def _ordered_weights(counts: Counter[str], order: Mapping[str, int]) -> list[tuple[str, int]]:
    return sorted(counts.items(), key=lambda item: (-item[1], order[item[0]]))


def build_search(
    matches: Sequence[Athlete],
    contests: Sequence[ContestRow],
    scores: Sequence[ScoreRow],
    catalogue: Catalogue,
    limit: int,
) -> AthleteSearch:
    order = sort_orders(catalogue.weights)
    categories = {w.code: w for w in catalogue.weights}
    weights = _contest_weights(contests)
    n_scores = Counter(s.athlete_id for s in distinct(scores))
    rows = [
        SearchRow(
            a,
            tuple(weight_ref(categories[w]) for w, _ in _ordered_weights(weights.get(a.id, Counter()), order)),
            n_scores[a.id],
        )
        for a in matches
    ]
    rows.sort(key=lambda r: (-r.n_scores, r.athlete.family_name, r.athlete.given_name, r.athlete.id))
    return AthleteSearch(tuple(rows[:limit]))


def athlete_warnings(contests: Sequence[ContestRow], catalogue: Catalogue) -> tuple[WarningItem, ...]:
    rulesets = {r.id: r for r in catalogue.rulesets}
    found = []
    if len({(rulesets[c.ruleset_id].has_koka, rulesets[c.ruleset_id].has_yuko) for c in contests}) > 1:
        found.append(
            WarningItem(
                "mixed_score_scales",
                "This athlete's contests span rulesets with different score scales: "
                "ippon/waza-ari/yuko shares are not comparable.",
            )
        )
    flagged = sum(1 for c in contests if c.has_quality_issue)
    if flagged == 1:
        found.append(WarningItem("quality_issues", "1 of this athlete's contests has inconsistent IJF data."))
    elif flagged:
        found.append(WarningItem("quality_issues", f"{flagged} of this athlete's contests have inconsistent IJF data."))
    return tuple(found)


def _cosine(a: Mapping[int, int], b: Mapping[int, int]) -> float:
    dot = sum(n * b.get(k, 0) for k, n in a.items())
    norm = math.sqrt(sum(n * n for n in a.values()) * sum(n * n for n in b.values()))
    return dot / norm if norm else 0.0


def build_athlete(
    athlete: Athlete,
    scope: SimilarScope,
    min_scores: int,
    contests: Sequence[ContestRow],
    scores: Sequence[ScoreRow],
    catalogue: Catalogue,
    athletes: Mapping[int, Athlete],
    thresholds: Thresholds,
) -> AthleteResponse:
    """`contests` and `scores` are the whole database: the judoka page is not filtered, and the similar athletes
    are compared on their whole careers."""
    order = sort_orders(catalogue.weights)
    categories = {w.code: w for w in catalogue.weights}
    weights_of = _contest_weights(contests)
    own_contests = [c for c in contests if athlete.id in (c.white_athlete_id, c.blue_athlete_id)]
    own_scores = [s for s in scores if s.athlete_id == athlete.id]
    unique = distinct(own_scores)
    profiles: dict[int, Counter[int]] = {}
    ippons: Counter[int] = Counter()
    for s in scores:
        if s.technique_tag_id is not None:
            profiles.setdefault(s.athlete_id, Counter())[s.technique_tag_id] += 1
            if s.athlete_id == athlete.id and s.score_value == "ippon":
                ippons[s.technique_tag_id] += 1
    totals = Counter(s.athlete_id for s in distinct(scores))
    own_profile = profiles.get(athlete.id, Counter())
    main = main_technique(own_profile, ippons, catalogue.tags)
    weights = _ordered_weights(weights_of[athlete.id], order)
    main_weight = categories[weights[0][0]]
    contests_by_id = {c.id: c for c in own_contests}
    techniques = _techniques(own_scores, len(unique), catalogue)
    groups = tuple(
        ScoreGroup(
            t.technique,
            t.n,
            tuple(
                athlete_score_row(s, catalogue, contests_by_id, athletes)
                for s in newest_first(
                    [s for s in own_scores if _code(s.technique_tag_id, catalogue) == _code_of(t.technique)],
                    catalogue.competitions,
                )
            ),
        )
        for t in techniques
    )
    years = [c.year for c in own_contests]
    data = AthleteDetail(
        athlete=athlete,
        judobase_url=athlete_url(athlete.id),
        weights=tuple(AthleteWeight(weight_ref(categories[w]), n) for w, n in weights),
        years={"from": min(years), "to": max(years)},
        kpis=AthleteKpis(
            competitions=len({c.competition_id for c in own_contests}),
            contests=len(own_contests),
            scores=len(unique),
            techniques=len(own_profile),
            ippon_share=ratio(sum(1 for s in unique if s.score_value == "ippon"), len(unique)),
            main_technique=technique_ref(catalogue.tags[main]) if main is not None else None,
        ),
        sample=count_sample(len(unique), thresholds),
        techniques=techniques,
        score_groups=groups,
        similar=Similar(
            scope=scope,
            weight=weight_ref(main_weight),
            min_scores_athlete=min_scores,
            sample=count_sample(len(unique), thresholds),
            rows=_similar(
                athlete,
                own_profile,
                main_weight.code,
                scope,
                min_scores,
                weights_of,
                profiles,
                totals,
                catalogue,
                athletes,
                thresholds,
            ),
        ),
    )
    return AthleteResponse(athlete_warnings(own_contests, catalogue), data)


def _code(tag_id: int | None, catalogue: Catalogue) -> str | None:
    return catalogue.tags[tag_id].code if tag_id is not None else None


def _code_of(ref: TechniqueRef | None) -> str | None:
    return ref.code if ref else None


def _techniques(own_scores: Sequence[ScoreRow], total: int, catalogue: Catalogue) -> tuple[AthleteTechnique, ...]:
    rows = [
        AthleteTechnique(
            technique=technique_ref(catalogue.tags[g.tag_id]) if g.tag_id is not None else None,
            n=g.n,
            share_of_total=ratio(g.n, total),
            counts=g.counts(),
            pct=g.shares(),
            n_awasete=g.awasete,
            side=g.side_counts(),
        )
        for g in technique_groups(own_scores).values()
    ]
    rows.sort(key=lambda r: r.technique.name if r.technique else "")
    rows.sort(key=lambda r: r.n, reverse=True)
    rows.sort(key=lambda r: r.technique is None)
    return tuple(rows)


def _similar(
    athlete: Athlete,
    own_profile: Mapping[int, int],
    main_weight: str,
    scope: SimilarScope,
    min_scores: int,
    weights_of: Mapping[int, Counter[str]],
    profiles: Mapping[int, Counter[int]],
    totals: Mapping[int, int],
    catalogue: Catalogue,
    athletes: Mapping[int, Athlete],
    thresholds: Thresholds,
) -> tuple[SimilarAthlete, ...]:
    if not own_profile:
        return ()
    order = sort_orders(catalogue.weights)
    categories = {w.code: w for w in catalogue.weights}
    gender = categories[main_weight].gender
    rows = []
    for candidate, counts in weights_of.items():
        if candidate == athlete.id:
            continue
        their_weight = most_frequent_weight(counts, order)
        if categories[their_weight].gender != gender or (scope == "weight" and their_weight != main_weight):
            continue
        profile = profiles.get(candidate)
        if totals.get(candidate, 0) < min_scores or not profile:
            continue
        similarity = round4(_cosine(own_profile, profile))
        if not similarity:
            continue
        top = sorted(profile.items(), key=lambda item: (-item[1], catalogue.tags[item[0]].code))[:TOP_TECHNIQUES]
        rows.append(
            SimilarAthlete(
                athlete=athletes[candidate],
                weight=weight_ref(categories[their_weight]),
                similarity=similarity,
                n_scores=totals[candidate],
                top_techniques=tuple(
                    TopTechnique(t.code, t.name, t.group_label, t.domain, n)
                    for t, n in ((catalogue.tags[tag_id], n) for tag_id, n in top)
                ),
                sample=count_sample(totals[candidate], thresholds),
            )
        )
    rows.sort(key=lambda r: (-(r.similarity or 0.0), -r.n_scores, r.athlete.id))
    return tuple(rows[:MAX_SIMILAR])
