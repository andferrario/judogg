from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date

from judogg.app.domain.links import contest_url, judotv_url
from judogg.app.domain.model import Athlete, Catalogue, Competition, ContestRow, Direction, ScoreRow, ScoreValue
from judogg.app.domain.refs import TechniqueRef, WeightRef, weight_ref


@dataclass(frozen=True)
class CompetitionRef:
    id: int
    name: str


@dataclass(frozen=True)
class AthleteScoreRow:
    date: date
    competition: CompetitionRef
    weight: WeightRef
    opponent: Athlete
    score_value: ScoreValue
    is_awasete: bool
    direction: Direction
    is_gs: bool
    time_bin: int
    contest_code: str
    judobase_url: str
    judotv_url: str | None


@dataclass(frozen=True)
class ScoreListRow(AthleteScoreRow):
    athlete: Athlete


@dataclass(frozen=True)
class TechniqueScores:
    technique: TechniqueRef
    rows: tuple[ScoreListRow, ...]
    page: int
    page_size: int
    total: int


def newest_first(scores: Sequence[ScoreRow], competitions: Mapping[int, Competition]) -> list[ScoreRow]:
    return sorted(
        scores, key=lambda s: (competitions[s.competition_id].date_from, s.contest_id, s.event_id), reverse=True
    )


def athlete_score_row(
    score: ScoreRow, catalogue: Catalogue, contests: Mapping[int, ContestRow], athletes: Mapping[int, Athlete]
) -> AthleteScoreRow:
    competition = catalogue.competitions[score.competition_id]
    code = contests[score.contest_id].code
    category = next(w for w in catalogue.weights if w.code == score.weight)
    return AthleteScoreRow(
        date=competition.date_from,
        competition=CompetitionRef(competition.id, competition.name),
        weight=weight_ref(category),
        opponent=athletes[score.opponent_id],
        score_value=score.score_value,
        is_awasete=score.is_awasete,
        direction=score.direction,
        is_gs=score.is_gs,
        time_bin=score.time_bin,
        contest_code=code,
        judobase_url=contest_url(code),
        judotv_url=judotv_url(competition.code, code),
    )


def score_list_row(
    score: ScoreRow, catalogue: Catalogue, contests: Mapping[int, ContestRow], athletes: Mapping[int, Athlete]
) -> ScoreListRow:
    base = athlete_score_row(score, catalogue, contests, athletes)
    return ScoreListRow(**vars(base), athlete=athletes[score.athlete_id])
