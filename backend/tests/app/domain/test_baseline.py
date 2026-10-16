from app_fakes import score

from judogg.app.domain.baseline import category_shares, expected_share
from judogg.app.domain.model import ScoreRow


def scores() -> list[ScoreRow]:
    return [
        score(event_id=1, weight="m-66", technique_tag_id=1),
        score(event_id=2, weight="m-66", technique_tag_id=2),
        score(event_id=3, weight="m-81", technique_tag_id=1),
        score(event_id=4, weight="m-81", technique_tag_id=1),
        score(event_id=5, weight="m-81", technique_tag_id=1),
        score(event_id=6, weight="m-81", technique_tag_id=None),
    ]


def test_expected_share_weights_the_category_shares() -> None:
    shares = category_shares(scores())
    assert expected_share(shares, {"m-66": 1, "m-81": 3}, 4, 1) == 0.25 * 0.5 + 0.75 * 0.75
    assert expected_share(shares, {"m-81": 1}, 1, None) == 0.25


def test_with_one_category_the_expected_share_is_the_plain_share() -> None:
    only_81 = [s for s in scores() if s.weight == "m-81"]
    assert expected_share(category_shares(only_81), {"m-81": 2}, 2, 1) == 3 / 4


def test_a_category_without_scores_adds_nothing() -> None:
    assert expected_share(category_shares(scores()), {"m-90": 5}, 5, 1) == 0.0
