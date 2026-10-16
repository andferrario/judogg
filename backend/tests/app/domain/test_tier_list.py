import pytest
from app_fakes import THRESHOLDS, score

from judogg.app.domain.model import Tag
from judogg.app.domain.techniques import SORT_KEYS, SortKey, build_tier_list

TAGS = {
    1: Tag(1, "seoi_nage", "Seoi-nage", "technique", "Te-waza", "standing"),
    2: Tag(2, "uchi_mata", "Uchi-mata", "technique", "Ashi-waza", "standing"),
    3: Tag(3, "o_goshi", "O-goshi", "technique", "Koshi-waza", "standing"),
}
SCORES = [
    score(event_id=1, technique_tag_id=1, score_value="ippon"),
    score(event_id=2, technique_tag_id=1, athlete_id=11, score_value="yuko"),
    score(event_id=3, technique_tag_id=2, athlete_id=12, score_value="ippon"),
    score(event_id=4, technique_tag_id=3, athlete_id=13, score_value="waza_ari"),
    score(event_id=5, technique_tag_id=None, athlete_id=14),
    score(event_id=6, technique_tag_id=None, athlete_id=14),
    score(event_id=7, technique_tag_id=None, athlete_id=14),
]


def codes(sort: SortKey, order: str = "desc", limit: int = 50, count_by: str = "event") -> list[str | None]:
    tier = build_tier_list(SCORES, TAGS, count_by, sort, order, limit, THRESHOLDS)  # type: ignore[arg-type]
    return [row.technique.code if row.technique else None for row in tier.rows]


def test_share_desc_with_ties_by_scores_then_name_and_unknown_last() -> None:
    assert codes("share") == ["seoi_nage", "o_goshi", "uchi_mata", None]


def test_share_by_athlete() -> None:
    tier = build_tier_list(SCORES, TAGS, "athlete", "share", "desc", 50, THRESHOLDS)
    assert [(r.technique.code if r.technique else None, r.share) for r in tier.rows] == [
        ("seoi_nage", 0.4),
        ("o_goshi", 0.2),
        ("uchi_mata", 0.2),
        (None, 0.2),
    ]


@pytest.mark.parametrize("sort", SORT_KEYS)
def test_every_sort_key_keeps_the_unknown_row_last(sort: SortKey) -> None:
    for order in ("asc", "desc"):
        assert codes(sort, order)[-1] is None


def test_ascending_percent_ippon() -> None:
    assert codes("pct_ippon", "asc") == ["o_goshi", "seoi_nage", "uchi_mata", None]


def test_limit_and_total_rows() -> None:
    tier = build_tier_list(SCORES, TAGS, "event", "share", "desc", 2, THRESHOLDS)
    assert (len(tier.rows), tier.total_rows) == (2, 4)


def test_tier_list_without_scores() -> None:
    tier = build_tier_list([], TAGS, "event", "share", "desc", 50, THRESHOLDS)
    assert (tier.rows, tier.total_rows, tier.sample.status) == ((), 0, "insufficient")
