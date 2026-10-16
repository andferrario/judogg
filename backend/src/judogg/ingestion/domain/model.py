from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Literal

RawJson = Mapping[str, Any]

Gender = Literal["m", "f"]
ScoreValue = Literal["ippon", "waza_ari", "yuko"]
Domain = Literal["standing", "ground"]
TechniqueDomain = Literal["standing", "ground", "unknown"]
Direction = Literal["left", "right", "unknown"]
PenaltyKind = Literal["shido", "hansoku_shido"]
TagKind = Literal["technique", "shido_reason"]
Level = Literal["elite", "continental"]
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
IssueCode = Literal[
    "summary_mismatch", "unknown_event_type", "unknown_actor", "new_tag_group", "unknown_weight", "no_events"
]


@dataclass(frozen=True)
class RulesetKey:
    has_koka: bool
    has_yuko: bool
    max_wazaari: int | None
    max_shido: int


@dataclass(frozen=True)
class Ruleset:
    id: int
    key: RulesetKey
    year_from: int
    year_to: int
    label: str


@dataclass(frozen=True)
class Competition:
    id: int
    code: str | None
    name: str
    rank_name: str
    date_from: date
    date_to: date
    year: int
    ruleset_id: int
    level: Level
    exclusion_reason: str | None


@dataclass(frozen=True)
class Athlete:
    id: int
    family_name: str
    given_name: str
    country_code: str


@dataclass(frozen=True)
class Tag:
    id: int
    code: str
    name: str
    kind: TagKind
    group_label: str | None
    domain: Domain | None


@dataclass(frozen=True)
class ContestDims:
    competition_id: int
    year: int
    ruleset_id: int
    gender: Gender
    weight_category_id: int


@dataclass(frozen=True)
class Contest:
    id: int
    code: str
    dims: ContestDims
    white_athlete_id: int
    blue_athlete_id: int
    white_country_code: str
    blue_country_code: str
    end_type: EndType
    went_gs: bool
    duration_s: int
    has_quality_issue: bool


@dataclass(frozen=True)
class Score:
    event_id: int
    contest_id: int
    dims: ContestDims
    athlete_id: int
    athlete_country: str
    opponent_id: int
    score_value: ScoreValue
    is_awasete: bool
    technique_tag_id: int | None
    technique_domain: TechniqueDomain
    direction: Direction
    is_gs: bool
    time_bin: int


@dataclass(frozen=True)
class Penalty:
    event_id: int
    contest_id: int
    dims: ContestDims
    athlete_id: int
    athlete_country: str
    penalty_kind: PenaltyKind
    shido_number: int
    reason_tag_id: int | None
    is_gs: bool
    time_bin: int


@dataclass(frozen=True)
class QualityIssue:
    code: IssueCode
    contest_id: int | None
    event_id: int | None
    detail: Mapping[str, str | int] = field(default_factory=dict)


@dataclass(frozen=True)
class ParsedContest:
    contest: Contest
    athletes: tuple[Athlete, Athlete]
    scores: tuple[Score, ...]
    penalties: tuple[Penalty, ...]
    tags: tuple[Tag, ...]
    issues: tuple[QualityIssue, ...]
    n_events: int


@dataclass(frozen=True)
class SkippedContest:
    reason: str
    issue: QualityIssue | None = None


@dataclass(frozen=True)
class Inclusion:
    exclusion_reason: str | None
    tag_coverage: Decimal | None
    contests: tuple[ParsedContest, ...]
    issues: tuple[QualityIssue, ...]
