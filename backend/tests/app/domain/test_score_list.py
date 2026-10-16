from datetime import date

from app_fakes import catalogue, contest, score

from judogg.app.domain.model import Athlete, Competition
from judogg.app.domain.score_list import newest_first, score_list_row


def competition(id_: int, day: int, code: str | None = "c") -> Competition:
    return Competition(
        id_, code, f"C{id_}", "Grand Prix", "elite", date(2025, 1, day), date(2025, 1, day), 2025, 2025, None, None
    )


COMPETITIONS = {1: competition(1, 1), 2: competition(2, 9, code=None)}


def test_newest_competition_then_contest_then_event_first() -> None:
    rows = [
        score(event_id=1, contest_id=1, competition_id=1),
        score(event_id=5, contest_id=2, competition_id=2),
        score(event_id=9, contest_id=2, competition_id=2),
        score(event_id=2, contest_id=3, competition_id=1),
    ]
    assert [s.event_id for s in newest_first(rows, COMPETITIONS)] == [9, 5, 2, 1]


def test_row_without_competition_code_has_no_judotv_link() -> None:
    athletes = {10: Athlete(10, "A", "B", "ITA"), 20: Athlete(20, "C", "D", "FRA")}
    row = score_list_row(
        score(competition_id=2), catalogue(competitions=COMPETITIONS), {1: contest(code="x_1")}, athletes
    )
    assert (row.date, row.contest_code, row.judotv_url) == (date(2025, 1, 9), "x_1", None)
    assert row.judobase_url.endswith("/x_1")
