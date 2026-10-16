from app_fakes import THRESHOLDS, catalogue, filters, score

from judogg.app.domain.model import Athlete, ScoreRow, Tag
from judogg.app.domain.repertoire import build_pairs, build_repertoire

TAGS = {
    1: Tag(1, "uchi_mata", "Uchi-mata", "technique", "Ashi-waza", "standing"),
    2: Tag(2, "seoi_nage", "Seoi-nage", "technique", "Te-waza", "standing"),
    3: Tag(3, "o_goshi", "O-goshi", "technique", "Koshi-waza", "standing"),
}
ATHLETES = {i: Athlete(i, f"G{i}", f"F{i}", "ITA") for i in range(10, 30)}


def athlete_scores(athlete: int, techniques: list[int], weight: str = "m-73") -> list[ScoreRow]:
    return [
        score(event_id=athlete * 100 + i, athlete_id=athlete, technique_tag_id=t, weight=weight)
        for i, t in enumerate(techniques)
    ]


def test_nobody_eligible() -> None:
    scores = athlete_scores(10, [1, 2])
    rep = build_repertoire(
        TAGS[1], None, scores, filters(min_scores_athlete=50), catalogue(tags=TAGS), ATHLETES, THRESHOLDS
    )
    assert (rep.cohort.eligible, rep.cohort.with_technique, rep.companions, rep.pair_athletes) == (0, 0, (), None)
    pairs = build_pairs(scores, filters(min_scores_athlete=50), catalogue(tags=TAGS), 10, THRESHOLDS)
    assert (pairs.eligible, pairs.pairs, pairs.matrix.techniques) == (0, (), ())


def test_companion_lift_and_pair_athletes() -> None:
    scores = athlete_scores(10, [1, 1, 2, 2]) + athlete_scores(11, [1, 1, 3, 3]) + athlete_scores(12, [2, 2, 3, 3])
    rep = build_repertoire(
        TAGS[1], TAGS[2], scores, filters(min_scores_athlete=2), catalogue(tags=TAGS), ATHLETES, THRESHOLDS
    )
    assert [(c.technique.code, c.n_both, c.p_given, c.p_base, c.lift) for c in rep.companions] == [
        ("o_goshi", 1, 0.5, 0.6667, 0.75),
        ("seoi_nage", 1, 0.5, 0.6667, 0.75),
    ]
    assert rep.pair_athletes is not None
    assert [(r.athlete.id, r.n_technique, r.n_with, r.n_total) for r in rep.pair_athletes.rows] == [(10, 2, 2, 4)]


def test_pair_order_ties_by_code_and_diagonal_is_null() -> None:
    scores = [s for a in range(10, 15) for s in athlete_scores(a, [1, 1, 2, 2])]
    pairs = build_pairs(scores, filters(min_scores_athlete=2), catalogue(tags=TAGS), 10, THRESHOLDS)
    (pair,) = pairs.pairs
    assert (pair.a.code, pair.b.code, pair.n_both, pair.support, pair.confidence, pair.lift) == (
        "seoi_nage",
        "uchi_mata",
        5,
        1.0,
        1.0,
        1.0,
    )
    assert pairs.matrix.cells[0][0] is None and pairs.matrix.cells[0][1] is not None


def test_techniques_below_the_thresholds_are_left_out() -> None:
    scores = athlete_scores(10, [1, 1, 2]) + athlete_scores(11, [3, 3, 3])
    rep = build_repertoire(
        TAGS[1], None, scores, filters(min_scores_athlete=3), catalogue(tags=TAGS), ATHLETES, THRESHOLDS
    )
    assert (rep.cohort.eligible, rep.cohort.with_technique, rep.companions) == (2, 1, ())
    pairs = build_pairs(scores, filters(min_scores_athlete=3), catalogue(tags=TAGS), 10, THRESHOLDS)
    assert pairs.pairs == () and [t.code for t in pairs.matrix.techniques] == ["o_goshi", "uchi_mata"]
