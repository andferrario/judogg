import pytest
from app_fakes import catalogue

from judogg.app.application.errors import InvalidParameter
from judogg.app.application.filters import resolve_filters
from judogg.app.domain.model import Filters


def test_defaults() -> None:
    assert resolve_filters({}, catalogue()) == Filters(
        gender="all",
        weight=(),
        year_from=2017,
        year_to=2027,
        ruleset=(2017, 2018, 2025),
        country=(),
        side=("left", "right", "unknown"),
        domain=("standing", "ground", "unknown"),
        count_by="event",
        min_scores_athlete=5,
        min_scores_technique=2,
    )


def test_explicit_values() -> None:
    resolved = resolve_filters(
        {
            "gender": "m",
            "weight": "m-73,m-81",
            "ruleset": "2018,2025",
            "year_from": "2020",
            "year_to": "2026",
            "country": "jpn, fra",
            "side": "right",
            "domain": "ground,standing",
            "count_by": "athlete",
            "min_scores_athlete": "3",
            "min_scores_technique": "1",
        },
        catalogue(),
    )
    assert resolved == Filters(
        gender="m",
        weight=("m-73", "m-81"),
        year_from=2020,
        year_to=2026,
        ruleset=(2018, 2025),
        country=("JPN", "FRA"),
        side=("right",),
        domain=("ground", "standing"),
        count_by="athlete",
        min_scores_athlete=3,
        min_scores_technique=1,
    )


def test_selected_rulesets_give_the_default_years() -> None:
    resolved = resolve_filters({"ruleset": "2017,2018"}, catalogue())
    assert (resolved.year_from, resolved.year_to) == (2017, 2024)


def test_empty_values_mean_absent() -> None:
    resolved = resolve_filters({"gender": "", "weight": "m-73,,", "side": "", "count_by": ""}, catalogue())
    assert (resolved.gender, resolved.weight, resolved.side, resolved.count_by) == (
        "all",
        ("m-73",),
        ("left", "right", "unknown"),
        "event",
    )


def test_without_rulesets_there_is_no_ruleset_and_no_year() -> None:
    resolved = resolve_filters({}, catalogue(rulesets=()))
    assert (resolved.ruleset, resolved.year_from, resolved.year_to) == ((), None, None)


@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({"gender": "x"}, "gender"),
        ({"weight": "m-75"}, "weight"),
        ({"gender": "f", "weight": "m-73"}, "weight"),
        ({"ruleset": "1999"}, "ruleset"),
        ({"ruleset": "abc"}, "ruleset"),
        ({"ruleset": "²"}, "ruleset"),
        ({"ruleset": "9" * 5000}, "ruleset"),
        ({"ruleset": "٢٠٢٥"}, "ruleset"),
        ({"min_scores_athlete": "\uff13"}, "min_scores_athlete"),  # fullwidth 3
        ({"year_from": "2_020"}, "year_from"),
        ({"year_to": "+2025"}, "year_to"),
        ({"year_from": "1800"}, "year_from"),
        ({"year_to": "two"}, "year_to"),
        ({"year_from": "2026", "year_to": "2025"}, "year_from"),
        ({"country": "JP"}, "country"),
        ({"side": "up"}, "side"),
        ({"domain": "air"}, "domain"),
        ({"count_by": "contest"}, "count_by"),
        ({"min_scores_athlete": "0"}, "min_scores_athlete"),
        ({"min_scores_technique": "11"}, "min_scores_technique"),
    ],
)
def test_invalid_parameters(params: dict[str, str], field: str) -> None:
    with pytest.raises(InvalidParameter) as error:
        resolve_filters(params, catalogue())
    assert error.value.field == field
