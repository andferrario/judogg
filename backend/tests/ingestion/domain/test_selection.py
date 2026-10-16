from datetime import date
from typing import Any

import pytest
from ijf_helpers import exclusion_rules, load_fixture

from judogg.ingestion.domain.competitions import InvalidCompetitionEntry
from judogg.ingestion.domain.selection import (
    InvalidSelection,
    Selection,
    Wanted,
    category_weight_ids,
    months_before,
    parse_years,
    select_competitions,
)

TODAY = date(2026, 10, 13)


def entry(competition_id: int, **overrides: str) -> dict[str, Any]:
    values = {
        "id_competition": str(competition_id),
        "name": f"Grand Prix {competition_id}",
        "rank_name": "Grand Prix",
        "comp_year": "2025",
        "has_results": "100",
        "date_from": "2025/03/01",
        "date_to": "2025/03/03",
    }
    return values | overrides


def select(listing: list[dict[str, Any]], **selection: Any) -> list[Wanted]:
    return select_competitions(listing, Selection(**selection), TODAY, exclusion_rules())


@pytest.mark.parametrize(
    ("text", "years"),
    [("2025", {2025}), ("2025, 2026", {2025, 2026}), ("2020-2022", {2020, 2021, 2022}), ("2017", {2017})],
)
def test_parse_years(text: str, years: set[int]) -> None:
    assert parse_years(text) == years


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("2016", "before 2017"),
        ("2015-2018", "before 2017"),
        ("2022-2020", "backwards"),
        ("abc", "not a year"),
        ("", "not a year"),
    ],
)
def test_bad_years(text: str, message: str) -> None:
    with pytest.raises(InvalidSelection, match=message):
        parse_years(text)


@pytest.mark.parametrize(
    ("day", "months", "expected"),
    [
        (date(2026, 5, 31), 3, date(2026, 2, 28)),
        (date(2024, 5, 31), 3, date(2024, 2, 29)),
        (date(2026, 1, 15), 12, date(2025, 1, 15)),
        (date(2026, 10, 13), 1, date(2026, 9, 13)),
    ],
)
def test_months_before_clamps_the_day(day: date, months: int, expected: date) -> None:
    assert months_before(day, months) == expected


def test_years_select_finished_competitions_with_results_that_no_rule_excludes() -> None:
    listing = [
        entry(1),
        entry(2, comp_year="2024", date_from="2024/03/01", date_to="2024/03/03"),
        entry(3, has_results="0"),
        entry(4, name="European Kata Championships"),
        entry(5, rank_name="Kata Tournament"),
        entry(6, comp_year="2026", date_from="2026/10/12", date_to="2026/10/13"),  # ends today: not finished
    ]
    assert [w.id for w in select(listing, years=frozenset({2025, 2026}))] == [1]


def test_recent_months_select_by_start_date_and_ask_for_a_refresh() -> None:
    listing = [
        entry(1, comp_year="2026", date_from="2026/05/01", date_to="2026/05/03"),
        entry(2, comp_year="2026", date_from="2026/04/12", date_to="2026/04/14"),
    ]
    assert select(listing, recent_months=6) == [Wanted(1, "Grand Prix 1", refresh=True)]


def test_the_options_select_the_union() -> None:
    listing = [
        entry(1),
        entry(2, comp_year="2026", date_from="2026/09/01", date_to="2026/09/03"),
        entry(3, has_results="0"),
    ]
    wanted = select(listing, years=frozenset({2025}), recent_months=2, competition_ids=(3,))
    assert [(w.id, w.refresh) for w in wanted] == [(1, False), (3, False), (2, True)]


def test_explicit_ids_skip_the_filters() -> None:
    listing = [entry(1, has_results="0", name="Kata Open", date_to="2026/12/01")]
    assert select(listing, competition_ids=(1,)) == [Wanted(1, "Kata Open", refresh=False)]


@pytest.mark.parametrize(
    ("listing", "message"),
    [([entry(1)], "competition 9 is not in the IJF competitions list"), ([entry(9, comp_year="2016")], "before 2017")],
)
def test_bad_explicit_ids(listing: list[dict[str, Any]], message: str) -> None:
    with pytest.raises(InvalidSelection, match=message):
        select(listing, competition_ids=(9,))


def test_malformed_entry_is_an_invalid_entry() -> None:
    with pytest.raises(InvalidCompetitionEntry, match="competition 1"):
        select([entry(1, date_to="soon")], years=frozenset({2025}))


def test_older_entries_are_never_read() -> None:
    assert select([entry(1, comp_year="1999", date_to="?")], years=frozenset({2025})) == []


def test_selection_is_empty_without_options() -> None:
    assert Selection().is_empty and not Selection(recent_months=1).is_empty


def test_category_weight_ids() -> None:
    assert category_weight_ids(load_fixture("minor/02_categories_1439.json")) == ["1", "2", "3", "4", "5", "6", "7"]
    assert category_weight_ids([]) == []
    assert category_weight_ids({"1": {"gender": "m"}, "2": "x"}) == []


def test_unreadable_id_is_an_invalid_entry() -> None:
    with pytest.raises(InvalidCompetitionEntry, match="abc"):
        select([entry(1) | {"id_competition": "abc"}], years=frozenset({2025}))
