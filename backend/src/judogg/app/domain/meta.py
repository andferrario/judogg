from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date

from judogg.app.domain.model import (
    DEFAULT_MIN_SCORES_ATHLETE,
    DEFAULT_MIN_SCORES_TECHNIQUE,
    Catalogue,
    ContestRow,
    CountBy,
    Gender,
    GenderFilter,
    IssueRow,
    Level,
    Ruleset,
    ScoreRow,
    TableCounts,
    Thresholds,
)
from judogg.app.domain.numbers import ratio
from judogg.app.domain.refs import ReasonRef, TechniqueRef, reason_ref, technique_ref
from judogg.app.domain.scores import distinct


@dataclass(frozen=True)
class GlossaryEntry:
    term: str
    definition: str


@dataclass(frozen=True)
class GenderOption:
    code: Gender
    label: str


GENDERS = (GenderOption("m", "Men"), GenderOption("f", "Women"))


@dataclass(frozen=True)
class WeightOption:
    code: str
    gender: Gender
    label: str
    contests: int


@dataclass(frozen=True)
class RulesetOption:
    id: int
    label: str
    year_from: int
    year_to: int
    has_koka: bool
    has_yuko: bool
    max_wazaari: int | None
    max_shido: int
    contests: int
    is_default: bool


@dataclass(frozen=True)
class Defaults:
    gender: GenderFilter
    ruleset: tuple[int, ...]
    year_from: int | None
    year_to: int | None
    count_by: CountBy
    min_scores_athlete: int
    min_scores_technique: int


@dataclass(frozen=True)
class WeightContests:
    weight: str
    contests: int


@dataclass(frozen=True)
class CoverageCompetition:
    id: int
    code: str | None
    name: str
    rank_name: str
    level: Level
    date_from: date
    date_to: date
    ruleset_id: int
    tag_coverage: float | None
    contests: int
    by_weight: tuple[WeightContests, ...]


@dataclass(frozen=True)
class ExcludedCompetition:
    id: int
    name: str
    year: int
    level: Level
    tag_coverage: float | None
    reason: str


@dataclass(frozen=True)
class CoverageTotals:
    competitions: int
    contests: int
    scores: int
    penalties: int
    athletes: int
    continental_score_share: float | None


@dataclass(frozen=True)
class Coverage:
    competitions: tuple[CoverageCompetition, ...]
    excluded: tuple[ExcludedCompetition, ...]
    totals: CoverageTotals


@dataclass(frozen=True)
class QualityIssueCount:
    code: str
    issues: int
    contests: int


@dataclass(frozen=True)
class Meta:
    genders: tuple[GenderOption, ...]
    weights: tuple[WeightOption, ...]
    rulesets: tuple[RulesetOption, ...]
    years: tuple[int, ...]
    countries: tuple[str, ...]
    techniques: tuple[TechniqueRef, ...]
    shido_reasons: tuple[ReasonRef, ...]
    defaults: Defaults
    thresholds: Thresholds
    coverage: Coverage
    quality_issues: tuple[QualityIssueCount, ...]
    glossary: tuple[GlossaryEntry, ...]


def build_meta(
    catalogue: Catalogue,
    contests: Sequence[ContestRow],
    scores: Sequence[ScoreRow],
    counts: TableCounts,
    issues: Sequence[IssueRow],
    thresholds: Thresholds,
    glossary: tuple[GlossaryEntry, ...],
) -> Meta:
    rulesets_in_order = sorted(catalogue.rulesets, key=lambda r: r.year_from, reverse=True)
    all_rulesets = sorted(catalogue.rulesets, key=lambda r: r.year_from)
    contests_per_weight = Counter(c.weight for c in contests)
    tags = sorted(catalogue.tags.values(), key=lambda t: t.name)
    return Meta(
        genders=GENDERS,
        weights=tuple(WeightOption(w.code, w.gender, w.label, contests_per_weight[w.code]) for w in catalogue.weights),
        rulesets=tuple(_ruleset_option(r, is_default=True) for r in rulesets_in_order),
        years=tuple(sorted({c.year for c in contests})),
        countries=tuple(sorted({code for c in contests for code in (c.white_country_code, c.blue_country_code)})),
        techniques=tuple(technique_ref(t) for t in tags if t.kind == "technique"),
        shido_reasons=tuple(reason_ref(t) for t in tags if t.kind == "shido_reason"),
        defaults=Defaults(
            gender="all",
            ruleset=tuple(r.id for r in all_rulesets),
            year_from=min((r.year_from for r in all_rulesets), default=None),
            year_to=max((r.year_to for r in all_rulesets), default=None),
            count_by="event",
            min_scores_athlete=DEFAULT_MIN_SCORES_ATHLETE,
            min_scores_technique=DEFAULT_MIN_SCORES_TECHNIQUE,
        ),
        thresholds=thresholds,
        coverage=_coverage(catalogue, contests, scores, counts),
        quality_issues=_quality_issues(issues),
        glossary=glossary,
    )


def _ruleset_option(ruleset: Ruleset, is_default: bool = True) -> RulesetOption:
    return RulesetOption(
        ruleset.id,
        ruleset.label,
        ruleset.year_from,
        ruleset.year_to,
        ruleset.has_koka,
        ruleset.has_yuko,
        ruleset.max_wazaari,
        ruleset.max_shido,
        ruleset.contests,
        is_default,
    )


def _coverage(
    catalogue: Catalogue, contests: Sequence[ContestRow], scores: Sequence[ScoreRow], counts: TableCounts
) -> Coverage:
    per_competition: dict[int, Counter[str]] = {}
    for c in contests:
        per_competition.setdefault(c.competition_id, Counter())[c.weight] += 1
    order = {w.code: w.sort_order for w in catalogue.weights}
    loaded = sorted((catalogue.competitions[i] for i in per_competition), key=lambda c: (c.date_from, c.id))
    competitions = tuple(
        CoverageCompetition(
            c.id,
            c.code,
            c.name,
            c.rank_name,
            c.level,
            c.date_from,
            c.date_to,
            c.ruleset_id,
            c.tag_coverage,
            per_competition[c.id].total(),
            tuple(
                WeightContests(weight, n)
                for weight, n in sorted(per_competition[c.id].items(), key=lambda item: order[item[0]])
            ),
        )
        for c in loaded
    )
    excluded = []
    for competition in sorted(catalogue.competitions.values(), key=lambda c: (-c.year, c.name, c.id)):
        if competition.exclusion_reason is not None:
            excluded.append(
                ExcludedCompetition(
                    competition.id,
                    competition.name,
                    competition.year,
                    competition.level,
                    competition.tag_coverage,
                    competition.exclusion_reason,
                )
            )
    unique = distinct(scores)
    continental = sum(1 for s in unique if catalogue.competitions[s.competition_id].level == "continental")
    totals = CoverageTotals(
        len(competitions),
        len(contests),
        len(unique),
        counts.penalties,
        counts.athletes,
        ratio(continental, len(unique)),
    )
    return Coverage(competitions, tuple(excluded), totals)


def _quality_issues(issues: Iterable[IssueRow]) -> tuple[QualityIssueCount, ...]:
    per_code: Counter[str] = Counter()
    contests_per_code: dict[str, set[int]] = {}
    for issue in issues:
        per_code[issue.code] += 1
        contests = contests_per_code.setdefault(issue.code, set())
        if issue.contest_id is not None:
            contests.add(issue.contest_id)
    return tuple(QualityIssueCount(code, per_code[code], len(contests_per_code[code])) for code in sorted(per_code))
