from collections.abc import Collection
from dataclasses import replace
from typing import Any, cast

from judogg.app.domain.model import (
    Athlete,
    Catalogue,
    ContestRow,
    Filters,
    Gender,
    IssueRow,
    PenaltyRow,
    Ruleset,
    ScoreRow,
    TableCounts,
    Thresholds,
    WeightCategory,
)

_SCORE = ScoreRow(
    event_id=1,
    contest_id=1,
    competition_id=1,
    year=2025,
    weight="m-73",
    athlete_id=10,
    athlete_country="ITA",
    opponent_id=20,
    score_value="waza_ari",
    is_awasete=False,
    technique_tag_id=100,
    direction="left",
    is_gs=False,
    time_bin=0,
)
_CONTEST = ContestRow(
    id=1,
    code="x_0001",
    competition_id=1,
    year=2025,
    ruleset_id=2025,
    weight="m-73",
    white_athlete_id=10,
    blue_athlete_id=20,
    white_country_code="ITA",
    blue_country_code="FRA",
    end_type="ippon",
    went_gs=False,
    duration_s=120,
    has_quality_issue=False,
)
_PENALTY = PenaltyRow(
    event_id=1,
    contest_id=1,
    weight="m-73",
    athlete_id=10,
    penalty_kind="shido",
    shido_number=1,
    reason_tag_id=None,
    time_bin=0,
)
_FILTERS = Filters(
    gender="all",
    weight=(),
    year_from=2025,
    year_to=2027,
    ruleset=(2025,),
    country=(),
    side=("left", "right", "unknown"),
    domain=("standing", "ground", "unknown"),
    count_by="event",
    min_scores_athlete=5,
    min_scores_technique=2,
)


def score(**overrides: Any) -> ScoreRow:
    return replace(_SCORE, **overrides)


def contest(**overrides: Any) -> ContestRow:
    return replace(_CONTEST, **overrides)


def penalty(**overrides: Any) -> PenaltyRow:
    return replace(_PENALTY, **overrides)


def filters(**overrides: Any) -> Filters:
    return replace(_FILTERS, **overrides)


CATEGORY_CODES = (
    "m-60",
    "m-66",
    "m-73",
    "m-81",
    "m-90",
    "m-100",
    "m+100",
    "f-48",
    "f-52",
    "f-57",
    "f-63",
    "f-70",
    "f-78",
    "f+78",
)
WEIGHTS = tuple(
    WeightCategory(code, cast(Gender, code[0]), code[1:], order) for order, code in enumerate(CATEGORY_CODES, start=1)
)
RULESETS = (
    Ruleset(2017, "2017", 2017, 2017, False, False, None, 2, 0),
    Ruleset(2018, "2018–2024", 2018, 2024, False, False, 1, 2, 0),
    Ruleset(2025, "2025–", 2025, 2027, False, True, 1, 2, 556),
)


def catalogue(**overrides: Any) -> Catalogue:
    return replace(Catalogue(WEIGHTS, RULESETS, {}, {}), **overrides)


THRESHOLDS = Thresholds(
    sample_ok=20,
    sample_small=5,
    athlete_sample_ok=10,
    athlete_sample_small=5,
    specialist_share=0.4,
    min_scores_country=30,
    unknown_technique_warning=0.1,
)


class EmptyReader:
    def catalogue(self) -> Catalogue:
        return Catalogue(WEIGHTS, (), {}, {})

    def scores(self, filters: Filters | None) -> list[ScoreRow]:
        return []

    def contests(self, filters: Filters | None) -> list[ContestRow]:
        return []

    def penalties(self, filters: Filters | None) -> list[PenaltyRow]:
        return []

    def table_counts(self) -> TableCounts:
        return TableCounts(0, 0)

    def quality_issues(self) -> list[IssueRow]:
        return []

    def athletes(self, ids: Collection[int] | None) -> dict[int, Athlete]:
        return {}

    def search_athletes(self, term: str) -> list[Athlete]:
        return []

    def contests_of_athletes(self, ids: Collection[int]) -> list[ContestRow]:
        return []

    def scores_of_athletes(self, ids: Collection[int]) -> list[ScoreRow]:
        return []
