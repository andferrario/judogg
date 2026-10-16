from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Literal

Gender = Literal["m", "f"]
GenderFilter = Literal["m", "f", "all"]
CountBy = Literal["event", "athlete"]
ScoreValue = Literal["ippon", "waza_ari", "yuko"]
Direction = Literal["left", "right", "unknown"]
TechniqueDomain = Literal["standing", "ground", "unknown"]
Level = Literal["elite", "continental"]
PenaltyKind = Literal["shido", "hansoku_shido"]
TagKind = Literal["technique", "shido_reason"]
EndType = Literal[
    "fusen_gachi",
    "kiken_gachi",
    "double_hansoku",
    "ippon",
    "waza_ari_awasete",
    "hansoku_shido",
    "score_gs",
    "score_regulation",
]

GENDER_FILTERS: tuple[GenderFilter, ...] = ("m", "f", "all")
COUNT_BYS: tuple[CountBy, ...] = ("event", "athlete")
SIDES: tuple[Direction, ...] = ("left", "right", "unknown")
DOMAINS: tuple[TechniqueDomain, ...] = ("standing", "ground", "unknown")
SCORE_VALUES: tuple[ScoreValue, ...] = ("ippon", "waza_ari", "yuko")
WALKOVERS: frozenset[EndType] = frozenset({"fusen_gachi", "kiken_gachi"})
DEFAULT_MIN_SCORES_ATHLETE = 5
DEFAULT_MIN_SCORES_TECHNIQUE = 2


@dataclass(frozen=True, slots=True)
class ScoreRow:
    event_id: int
    contest_id: int
    competition_id: int
    year: int
    weight: str
    athlete_id: int
    athlete_country: str
    opponent_id: int
    score_value: ScoreValue
    is_awasete: bool
    technique_tag_id: int | None
    direction: Direction
    is_gs: bool
    time_bin: int


@dataclass(frozen=True, slots=True)
class ContestRow:
    id: int
    code: str
    competition_id: int
    year: int
    ruleset_id: int
    weight: str
    white_athlete_id: int
    blue_athlete_id: int
    white_country_code: str
    blue_country_code: str
    end_type: EndType
    went_gs: bool
    duration_s: int
    has_quality_issue: bool


@dataclass(frozen=True, slots=True)
class PenaltyRow:
    event_id: int
    contest_id: int
    weight: str
    athlete_id: int
    penalty_kind: PenaltyKind
    shido_number: int
    reason_tag_id: int | None
    time_bin: int


@dataclass(frozen=True)
class WeightCategory:
    code: str
    gender: Gender
    label: str
    sort_order: int


@dataclass(frozen=True)
class Ruleset:
    id: int
    label: str
    year_from: int
    year_to: int
    has_koka: bool
    has_yuko: bool
    max_wazaari: int | None
    max_shido: int
    contests: int


@dataclass(frozen=True)
class Tag:
    id: int
    code: str
    name: str
    kind: TagKind
    group_label: str | None
    domain: Literal["standing", "ground"] | None


@dataclass(frozen=True)
class Competition:
    id: int
    code: str | None
    name: str
    rank_name: str
    level: Level
    date_from: date
    date_to: date
    year: int
    ruleset_id: int
    tag_coverage: float | None
    exclusion_reason: str | None


@dataclass(frozen=True)
class Catalogue:
    weights: tuple[WeightCategory, ...]
    rulesets: tuple[Ruleset, ...]
    tags: Mapping[int, Tag]
    competitions: Mapping[int, Competition]


@dataclass(frozen=True)
class TableCounts:
    athletes: int
    penalties: int


@dataclass(frozen=True)
class IssueRow:
    code: str
    contest_id: int | None


@dataclass(frozen=True)
class Filters:
    gender: GenderFilter
    weight: tuple[str, ...]
    year_from: int | None
    year_to: int | None
    ruleset: tuple[int, ...]
    country: tuple[str, ...]
    side: tuple[Direction, ...]
    domain: tuple[TechniqueDomain, ...]
    count_by: CountBy
    min_scores_athlete: int
    min_scores_technique: int


@dataclass(frozen=True)
class Thresholds:
    sample_ok: int
    sample_small: int
    athlete_sample_ok: int
    athlete_sample_small: int
    specialist_share: float
    min_scores_country: int
    unknown_technique_warning: float


@dataclass(frozen=True)
class Athlete:
    id: int
    given_name: str
    family_name: str
    country_code: str
