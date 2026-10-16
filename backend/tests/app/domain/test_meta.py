from datetime import date

from app_fakes import THRESHOLDS, catalogue, contest, score

from judogg.app.domain.meta import build_meta
from judogg.app.domain.model import Competition, IssueRow, Level, TableCounts


def competition(id_: int, level: Level = "elite", reason: str | None = None) -> Competition:
    return Competition(
        id_, None, f"C{id_}", "Grand Prix", level, date(2025, 1, id_), date(2025, 1, id_), 2025, 2025, None, reason
    )


def test_empty_database() -> None:
    meta = build_meta(catalogue(rulesets=()), [], [], TableCounts(0, 0), [], THRESHOLDS, ())
    assert (meta.defaults.ruleset, meta.defaults.year_from, meta.defaults.year_to) == ((), None, None)
    assert meta.coverage.totals.continental_score_share is None
    assert (meta.years, meta.countries, meta.rulesets) == ((), (), ())


def test_issues_without_a_contest_count_as_issues_only() -> None:
    meta = build_meta(
        catalogue(),
        [],
        [],
        TableCounts(0, 0),
        [IssueRow("unknown_weight", None), IssueRow("unknown_weight", 7)],
        THRESHOLDS,
        (),
    )
    assert [(q.code, q.issues, q.contests) for q in meta.quality_issues] == [("unknown_weight", 2, 1)]


def test_continental_share_and_excluded_order() -> None:
    competitions = {1: competition(1), 2: competition(2, "continental"), 3: competition(3, reason="no events")}
    meta = build_meta(
        catalogue(competitions=competitions),
        [contest(competition_id=1), contest(id=2, competition_id=2)],
        [score(competition_id=1), score(event_id=2, competition_id=2), score(event_id=3, competition_id=2)],
        TableCounts(2, 0),
        [],
        THRESHOLDS,
        (),
    )
    assert meta.coverage.totals.continental_score_share == 0.6667
    assert [c.id for c in meta.coverage.competitions] == [1, 2]
    assert [(e.id, e.reason) for e in meta.coverage.excluded] == [(3, "no events")]
