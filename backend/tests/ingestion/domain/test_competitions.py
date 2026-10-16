from collections import Counter
from datetime import date

import pytest
from ijf_helpers import exclusion_rules, fixture_competitions, load_fixture

from judogg.ingestion.domain.competitions import (
    InvalidCompetitionEntry,
    RulesetConflict,
    build_competitions,
    competition_level,
    derive_rulesets,
    exclusion_reason,
)
from judogg.ingestion.domain.model import Ruleset, RulesetKey


def raw_competition(**overrides: str | None) -> dict[str, str | None]:
    values: dict[str, str | None] = {
        "id_competition": "1",
        "competition_code": "x2020",
        "name": "X Grand Prix",
        "rank_name": "Grand Prix",
        "date_from": "2020/03/01",
        "date_to": "2020/03/02",
        "comp_year": "2020",
        "has_koka": "0",
        "has_yuko": "0",
        "max_wazaari": "1",
        "max_shido": "2",
    }
    values.update(overrides)
    return values


def test_history_starts_in_2017_and_89_competitions_are_excluded() -> None:
    competitions = fixture_competitions()
    assert len(competitions) == 715
    reasons = Counter(c.exclusion_reason for c in competitions.values() if c.exclusion_reason)
    assert sum(reasons.values()) == 89
    assert sum(n for reason, n in reasons.items() if reason.startswith("rank_name")) == 76
    assert reasons["name contains IBSA"] == 8
    assert reasons["name contains Paralympic"] + reasons["name contains Deaf"] == 3
    assert reasons["name contains Ne-Waza"] == 2


def test_example_competitions() -> None:
    paris = fixture_competitions()[3131]
    assert paris.date_from == date(2026, 2, 7)
    assert (paris.year, paris.ruleset_id, paris.level, paris.exclusion_reason) == (2026, 2025, "elite", None)
    assert fixture_competitions()[2942].level == "continental"


def test_three_rulesets_with_year_ids() -> None:
    _, rulesets = build_competitions(load_fixture("01_competitions_list.json"), exclusion_rules())
    assert rulesets == [
        Ruleset(2017, RulesetKey(False, False, None, 2), 2017, 2017, "2017"),
        Ruleset(2018, RulesetKey(False, False, 1, 2), 2018, 2024, "2018–2024"),
        Ruleset(2025, RulesetKey(False, True, 1, 2), 2025, 2027, "2025–"),
    ]


def test_two_rulesets_starting_in_the_same_year_fail() -> None:
    with pytest.raises(RulesetConflict):
        derive_rulesets([raw_competition(), raw_competition(id_competition="2", has_yuko="1")])


@pytest.mark.parametrize(
    ("name", "rank_name", "expected"),
    [
        ("Paris Grand Slam 2026", "Grand Slam", None),
        ("World Kata Championships", "Other events", "name contains Kata"),
        ("Mixed Team Championships", "Mixed Teams", "rank_name Mixed Teams"),
        ("IBSA Judo Grand Prix", "Other events", "name contains IBSA"),
    ],
)
def test_exclusion_reason(name: str, rank_name: str, expected: str | None) -> None:
    assert exclusion_reason(name, rank_name, exclusion_rules()) == expected


@pytest.mark.parametrize(
    ("rank_name", "level"),
    [
        ("Olympic Games", "elite"),
        ("World Championships", "elite"),
        ("Masters", "elite"),
        ("Grand Slam", "elite"),
        ("Grand Prix", "elite"),
        ("European Championships", "elite"),
        ("Asian Championships", "elite"),
        ("African Championships", "elite"),
        ("Panamerica Championships", "elite"),
        ("Oceanian Championships", "elite"),
        ("European Open", "continental"),
        ("Continental Cup", "continental"),
        ("Other events", "continental"),
        ("Something new", "continental"),
    ],
)
def test_competition_level(rank_name: str, level: str) -> None:
    assert competition_level(rank_name) == level


def test_missing_code_is_none() -> None:
    competitions, _ = build_competitions(
        [raw_competition(competition_code=None), raw_competition(id_competition="2", competition_code="")],
        exclusion_rules(),
    )
    assert [c.code for c in competitions] == [None, None]


def test_competitions_before_2017_are_ignored() -> None:
    competitions, rulesets = build_competitions([raw_competition(comp_year="2016", has_yuko="1")], exclusion_rules())
    assert (competitions, rulesets) == ([], [])


@pytest.mark.parametrize(
    "overrides",
    [{"max_shido": None}, {"date_from": "2020-03-01"}, {"comp_year": "twenty"}],
)
def test_unreadable_entry_names_the_competition(overrides: dict[str, str | None]) -> None:
    with pytest.raises(InvalidCompetitionEntry, match="competition 77"):
        build_competitions([raw_competition(id_competition="77", **overrides)], exclusion_rules())


@pytest.mark.parametrize("field", ["name", "rank_name"])
def test_null_name_or_rank_is_an_invalid_entry(field: str) -> None:
    entries = [dict(e) for e in load_fixture("01_competitions_list.json")]
    next(e for e in entries if e["id_competition"] == "3131")[field] = None
    with pytest.raises(InvalidCompetitionEntry, match=rf"competition 3131: .*{field}"):
        build_competitions(entries, exclusion_rules())
