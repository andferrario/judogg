from app_fakes import THRESHOLDS, catalogue, filters, score

from judogg.app.domain.counters import build_counters
from judogg.app.domain.model import Athlete, ScoreRow, Tag

TAGS = {
    1: Tag(1, "uchi_mata", "Uchi-mata", "technique", "Ashi-waza", "standing"),
    2: Tag(2, "seoi_nage", "Seoi-nage", "technique", "Te-waza", "standing"),
}
ATHLETES = {i: Athlete(i, f"G{i}", f"F{i}", "ITA") for i in range(10, 40)}


def scores() -> list[ScoreRow]:
    specialist = [score(event_id=i, athlete_id=10, technique_tag_id=1) for i in range(5)]
    against = [
        score(event_id=100, athlete_id=20, opponent_id=10, technique_tag_id=2),
        score(event_id=101, athlete_id=21, opponent_id=10, technique_tag_id=None),
        score(event_id=102, athlete_id=22, opponent_id=10, technique_tag_id=2),
    ]
    return specialist + against


def test_unknown_row_last_and_specialists() -> None:
    result = build_counters(
        TAGS[1], scores(), filters(min_scores_athlete=5), catalogue(tags=TAGS), ATHLETES, THRESHOLDS
    )
    assert [(s.athlete.id, s.share, s.n_total) for s in result.specialists.athletes] == [(10, 1.0, 5)]
    assert (result.conceded.n, [r.technique.code if r.technique else None for r in result.rows]) == (
        3,
        ["seoi_nage", None],
    )


def test_nobody_eligible() -> None:
    result = build_counters(
        TAGS[1], scores(), filters(min_scores_athlete=50), catalogue(tags=TAGS), ATHLETES, THRESHOLDS
    )
    assert (result.specialists.n, result.conceded.n, result.rows) == (0, 0, ())
