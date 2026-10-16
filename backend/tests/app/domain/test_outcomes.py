from app_fakes import THRESHOLDS, catalogue, contest, filters, penalty

from judogg.app.domain.outcomes import build_outcome_table


def test_shido_per_contest_counts_only_played_contests() -> None:
    table = build_outcome_table(
        [contest(id=1), contest(id=2, end_type="kiken_gachi")],
        [penalty(contest_id=1), penalty(event_id=2, contest_id=2)],
        filters(weight=("m-73", "m-81")),
        catalogue(),
        THRESHOLDS,
    )
    assert (table.total.played, table.total.shido_per_contest) == (1, 1.0)
    assert [r.weight.code for r in table.rows] == ["m-73", "m-81"]
    assert table.rows[1].shido_per_contest is None
