from app_fakes import THRESHOLDS, contest, filters, penalty, score

from judogg.app.domain.envelope import Totals, totals, warnings
from judogg.app.domain.model import Ruleset


def ruleset(year: int, has_yuko: bool, contests: int = 1) -> Ruleset:
    return Ruleset(year, str(year), year, year, False, has_yuko, 1, 2, contests)


def test_totals_count_what_is_behind_the_filters() -> None:
    contests = [contest(), contest(id=2, competition_id=2, white_athlete_id=10, blue_athlete_id=30)]
    scores = [score(technique_tag_id=1), score(technique_tag_id=2), score(event_id=2)]
    assert totals(scores, contests, [penalty(), penalty(event_id=2)]) == Totals(2, 2, 3, 2, 2)


def test_mixed_score_scales_only_among_rulesets_with_contests() -> None:
    rulesets = (ruleset(2018, False), ruleset(2025, True), ruleset(2017, False, contests=0))
    codes = [w.code for w in warnings(filters(ruleset=(2018, 2025)), rulesets, [], [], THRESHOLDS)]
    assert codes == ["mixed_score_scales"]
    assert warnings(filters(ruleset=(2017, 2025)), rulesets, [], [], THRESHOLDS) == ()


def test_high_unknown_technique_above_the_threshold() -> None:
    unknown = [score(event_id=i, technique_tag_id=None) for i in range(2)]
    known = [score(event_id=i) for i in range(2, 10)]
    (warning,) = warnings(filters(), (), unknown + known, [], THRESHOLDS)
    assert (warning.code, warning.message) == ("high_unknown_technique", "20% of the scores have no technique.")
    assert warnings(filters(), (), unknown[:1] + known + [score(event_id=11)], [], THRESHOLDS) == ()


def test_no_unknown_technique_warning_without_scores_to_analyse() -> None:
    assert warnings(filters(), (), None, [], THRESHOLDS) == ()
    assert warnings(filters(), (), [], [], THRESHOLDS) == ()


def test_quality_issues() -> None:
    one = warnings(filters(), (), [], [contest(has_quality_issue=True), contest(id=2)], THRESHOLDS)
    assert [(w.code, w.message) for w in one] == [
        ("quality_issues", "1 contest in the filter has inconsistent IJF data.")
    ]
    two = warnings(
        filters(), (), [], [contest(has_quality_issue=True), contest(id=2, has_quality_issue=True)], THRESHOLDS
    )
    assert two[0].message == "2 contests in the filter have inconsistent IJF data."
