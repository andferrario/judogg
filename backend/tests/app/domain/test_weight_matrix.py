from app_fakes import THRESHOLDS, catalogue, filters, score

from judogg.app.domain.model import Tag
from judogg.app.domain.weight_matrix import build_weight_matrix

TAGS = {
    1: Tag(1, "uchi_mata", "Uchi-mata", "technique", "Ashi-waza", "standing"),
    2: Tag(2, "seoi_nage", "Seoi-nage", "technique", "Te-waza", "standing"),
}


def test_by_athlete_counts_distinct_athletes() -> None:
    scores = [
        score(event_id=1, technique_tag_id=1),
        score(event_id=2, technique_tag_id=1),
        score(event_id=3, technique_tag_id=2, athlete_id=11),
    ]
    matrix = build_weight_matrix(
        scores, filters(count_by="athlete", weight=("m-73",)), catalogue(tags=TAGS), 8, THRESHOLDS
    )
    assert [t.code for t in matrix.techniques] == ["uchi_mata", "seoi_nage"]  # 1 athlete each: more scores first
    (row,) = matrix.rows
    assert (row.total, [(c.technique, c.n, c.share) for c in row.cells]) == (
        2,
        [("uchi_mata", 1, 0.5), ("seoi_nage", 1, 0.5)],
    )


def test_a_category_without_scores_has_null_shares() -> None:
    matrix = build_weight_matrix(
        [score(technique_tag_id=1)], filters(weight=("m-73", "m-81")), catalogue(tags=TAGS), 8, THRESHOLDS
    )
    assert matrix.rows[1].total == 0 and matrix.rows[1].cells[0].share is None
