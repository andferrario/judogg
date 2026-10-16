from judogg.app.domain.model import Ruleset
from judogg.app.domain.rulesets import default_ruleset


def ruleset(year_from: int, contests: int) -> Ruleset:
    return Ruleset(year_from, str(year_from), year_from, year_from, False, True, 1, 2, contests)


def test_the_most_recent_ruleset_with_contests_is_the_default() -> None:
    assert default_ruleset([ruleset(2018, 10), ruleset(2025, 3), ruleset(2017, 5)]) == ruleset(2025, 3)
    assert default_ruleset([ruleset(2018, 10), ruleset(2025, 0)]) == ruleset(2018, 10)


def test_without_contests_the_most_recent_ruleset_is_the_default() -> None:
    assert default_ruleset([ruleset(2018, 0), ruleset(2025, 0)]) == ruleset(2025, 0)


def test_without_rulesets_there_is_no_default() -> None:
    assert default_ruleset([]) is None
