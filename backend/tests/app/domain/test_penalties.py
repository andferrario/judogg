from app_fakes import THRESHOLDS, catalogue, contest, filters, penalty

from judogg.app.domain.model import Tag
from judogg.app.domain.penalties import build_penalties

TAGS = {
    5: Tag(5, "non_combativity", "Non-combativity", "shido_reason", "Passivity", None),
    6: Tag(6, "new_reason", "New-reason", "shido_reason", None, None),
}


def test_groups_without_label_and_without_reason() -> None:
    result = build_penalties(
        [penalty(reason_tag_id=5), penalty(event_id=2, reason_tag_id=6), penalty(event_id=3, reason_tag_id=None)],
        [contest()],
        filters(weight=("m-73",)),
        catalogue(tags=TAGS),
        THRESHOLDS,
    )
    assert [(g.group_label, g.n) for g in result.by_group] == [("Passivity", 1), ("Unknown group", 1), (None, 1)]
    assert [r.reason.code if r.reason else None for r in result.reasons] == ["new_reason", "non_combativity", None]


def test_fourth_shido_counts_as_third_and_deciding_ones() -> None:
    result = build_penalties(
        [penalty(shido_number=3, penalty_kind="hansoku_shido"), penalty(event_id=2, shido_number=4)],
        [contest(end_type="hansoku_shido")],
        filters(weight=("m-73",)),
        catalogue(tags=TAGS),
        THRESHOLDS,
    )
    assert [(b.number, b.n) for b in result.by_number] == [(1, 0), (2, 0), (3, 2)]
    assert (result.reasons[0].n_deciding, result.reasons[0].deciding_share) == (1, 0.5)
    assert (result.kpis.hansoku_share, result.kpis.shido_per_contest) == (1.0, 2.0)


def test_walkovers_are_not_played_contests() -> None:
    result = build_penalties(
        [penalty()], [contest(end_type="fusen_gachi")], filters(weight=("m-73",)), catalogue(tags=TAGS), THRESHOLDS
    )
    assert (result.kpis.played_contests, result.kpis.shido_per_contest, result.kpis.n_penalties) == (0, None, 1)
