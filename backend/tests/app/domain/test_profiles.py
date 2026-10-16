from app_fakes import WEIGHTS, score

from judogg.app.domain.categories import sort_orders
from judogg.app.domain.model import Tag
from judogg.app.domain.profiles import athlete_profiles

TAGS = {
    1: Tag(1, "uchi_mata", "Uchi-mata", "technique", "Ashi-waza", "standing"),
    2: Tag(2, "seoi_nage", "Seoi-nage", "technique", "Te-waza", "standing"),
}


def test_profile_counts_distinct_scores_and_technique_rows() -> None:
    scores = [
        score(event_id=1, technique_tag_id=1),
        score(event_id=1, technique_tag_id=2),
        score(event_id=2, technique_tag_id=None, weight="m-81"),
        score(event_id=3, technique_tag_id=2, weight="m-81", score_value="ippon"),
    ]
    profile = athlete_profiles(scores, TAGS, sort_orders(WEIGHTS))[10]
    assert (profile.total, dict(profile.techniques), dict(profile.ippons)) == (3, {1: 1, 2: 2}, {2: 1})
    assert (profile.main, profile.weight) == (2, "m-81")


def test_main_technique_ties_by_ippons_then_code() -> None:
    by_ippon = [score(event_id=1, technique_tag_id=1), score(event_id=2, technique_tag_id=2, score_value="ippon")]
    assert athlete_profiles(by_ippon, TAGS, sort_orders(WEIGHTS))[10].main == 2
    by_code = [score(event_id=1, technique_tag_id=1), score(event_id=2, technique_tag_id=2)]
    assert athlete_profiles(by_code, TAGS, sort_orders(WEIGHTS))[10].main == 2  # seoi_nage < uchi_mata


def test_athlete_without_known_technique_has_no_main() -> None:
    profile = athlete_profiles([score(technique_tag_id=None)], TAGS, sort_orders(WEIGHTS))[10]
    assert (profile.total, profile.main) == (1, None)
