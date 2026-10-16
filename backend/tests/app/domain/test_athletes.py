from datetime import date

from app_fakes import THRESHOLDS, catalogue, contest, score

from judogg.app.domain.athletes import athlete_warnings, build_athlete, build_search
from judogg.app.domain.model import Athlete, Competition, Tag

TAGS = {1: Tag(1, "uchi_mata", "Uchi-mata", "technique", "Ashi-waza", "standing")}
ATHLETES = {10: Athlete(10, "Anna", "Bianchi", "ITA"), 20: Athlete(20, "Carla", "Dupont", "FRA")}
COMPETITIONS = {
    1: Competition(1, "gp", "GP", "Grand Prix", "elite", date(2025, 3, 1), date(2025, 3, 2), 2025, 2025, None, None)
}


def test_search_ranks_by_scores_then_names() -> None:
    result = build_search(
        [ATHLETES[20], ATHLETES[10]],
        [contest(white_athlete_id=10, blue_athlete_id=20)],
        [score(athlete_id=20, technique_tag_id=None)],
        catalogue(),
        10,
    )
    assert [(r.athlete.id, r.n_scores, [w.code for w in r.weights]) for r in result.rows] == [
        (20, 1, ["m-73"]),
        (10, 0, ["m-73"]),
    ]


def test_athlete_without_known_technique_has_no_main_and_no_similar() -> None:
    response = build_athlete(
        ATHLETES[10],
        "weight",
        5,
        [contest()],
        [score(technique_tag_id=None)],
        catalogue(tags=TAGS, competitions=COMPETITIONS),
        ATHLETES,
        THRESHOLDS,
    )
    assert response.data.kpis.main_technique is None and response.data.similar.rows == ()
    assert response.data.years == {"from": 2025, "to": 2025}
    assert [g.technique for g in response.data.score_groups] == [None]


def test_warnings_for_mixed_scales_and_quality() -> None:
    contests = [contest(ruleset_id=2025, has_quality_issue=True), contest(id=2, ruleset_id=2018)]
    codes = [w.code for w in athlete_warnings(contests, catalogue())]
    assert codes == ["mixed_score_scales", "quality_issues"]
    two = [contest(has_quality_issue=True), contest(id=2, has_quality_issue=True)]
    assert "2 of this athlete's contests have" in athlete_warnings(two, catalogue())[0].message
