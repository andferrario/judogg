from typing import Any

import pytest
from ijf_helpers import (
    FIXTURES,
    FUSEN_GACHI,
    GUADALAJARA,
    KIKEN_GACHI,
    OTHER_WIN,
    fixture_competitions,
    fixture_contest,
    load_fixture,
    make_competition,
    parse_fixture,
    raw_contest,
    raw_event,
)

from judogg.ingestion.domain.model import Athlete, ContestDims, ParsedContest, QualityIssue, SkippedContest
from judogg.ingestion.domain.parser import parse_contest, sorted_events

COMPETITION = make_competition()


def parsed(raw: dict[str, Any]) -> ParsedContest:
    result = parse_contest(raw, COMPETITION)
    assert isinstance(result, ParsedContest)
    return result


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"age": "Juniors"}, "age Juniors"),
        ({"id_fight_team": "77"}, "team contest"),
        ({"is_finished": "0"}, "not finished"),
        ({"weight": "Open"}, "open weight"),
        ({"weight": " open "}, "open weight"),
    ],
)
def test_skipped_contests_write_nothing_but_say_why(overrides: dict[str, str], reason: str) -> None:
    assert parse_contest(raw_contest(**overrides), COMPETITION) == SkippedContest(reason)


@pytest.mark.parametrize(
    "overrides",
    [{"duration": None}, {"duration": "04:00"}, {"duration": ""}, {"fight_duration": None}, {"fight_duration": "x"}],
)
def test_contest_with_an_unreadable_duration_is_skipped(overrides: dict[str, str | None]) -> None:
    assert parse_contest(raw_contest(**overrides), COMPETITION) == SkippedContest("unreadable duration")


def test_unknown_weight_is_an_issue() -> None:
    result = parse_contest(raw_contest(weight="-75"), COMPETITION)
    issue = QualityIssue("unknown_weight", 1, None, {"gender": "m", "weight": "-75"})
    assert result == SkippedContest("unknown weight", issue)


def test_category_from_the_code_gender_and_the_weight() -> None:
    contest = parsed(raw_contest(contest_code_long="cont_open_por2017_f_0p78_0004", weight="+78")).contest
    assert contest.dims == ContestDims(1, 2025, 2025, "f", 14)


def test_all_556_example_contests_pass_and_map_to_the_14_categories() -> None:
    files = [
        GUADALAJARA,
        *(f"gs_fra2026/{p.name}" for p in sorted((FIXTURES / "gs_fra2026").glob("03_contests_*.json"))),
    ]
    categories = []
    for relative in files:
        for raw in load_fixture(relative)["contests"]:
            result = parse_contest(raw, fixture_competitions()[int(raw["id_competition"])])
            assert isinstance(result, ParsedContest)
            categories.append(result.contest.dims.weight_category_id)
    assert (len(categories), set(categories)) == (556, set(range(1, 15)))


def test_athletes_and_countries_come_from_the_contest() -> None:
    result = parsed(raw_contest())
    assert result.athletes == (Athlete(10, "WHITE", "Wanda", "ITA"), Athlete(20, "BLUE", "Bruno", "FRA"))
    assert (result.contest.white_country_code, result.contest.blue_country_code) == ("ITA", "FRA")


def test_events_are_ordered_by_clock_then_real_time_then_id() -> None:
    raw = fixture_contest("gs_fra2026/03_contests_w01_mu60.json", "gs_fra2026_0001_m_0060_0035")
    ids = [e["id_event"] for e in sorted_events(raw["events"])]
    assert ids.index("692712") < ids.index("692487")
    tie = [raw_event(3, "5", time_sc="10", time_real="20"), raw_event(2, "5", time_sc="10", time_real="20")]
    assert [e["id_event"] for e in sorted_events(tie)] == ["2", "3"]


def test_null_collections_are_empty() -> None:
    event = {**raw_event(1, "3"), "tags": None, "actors": None, "time_real": None}
    result = parsed(raw_contest(events=None))
    assert (result.n_events, result.scores, result.penalties) == (0, (), ())
    assert parsed(raw_contest(events=[event])).n_events == 1


@pytest.mark.parametrize(
    ("code", "end_type", "went_gs", "duration_s"),
    [
        ("gp_mex2025_0001_m_0066_0008", "hansoku_shido", False, 123),
        ("gp_mex2025_0001_m_0066_0021", "waza_ari_awasete", False, 214),
    ],
)
def test_outcome_of_example_contests(code: str, end_type: str, went_gs: bool, duration_s: int) -> None:
    contest = parse_fixture(GUADALAJARA, code).contest
    assert (contest.end_type, contest.went_gs, contest.duration_s) == (end_type, went_gs, duration_s)


def test_gs_flag_can_be_wrong() -> None:
    contest = parse_fixture("gs_fra2026/03_contests_w01_mu60.json", "gs_fra2026_0001_m_0060_0047").contest
    assert (contest.end_type, contest.went_gs, contest.duration_s) == ("score_gs", True, 245)


def test_double_hansoku_outcome() -> None:
    contest = parse_fixture("gs_fra2026/03_contests_w11_fu63.json", "gs_fra2026_0002_f_0063_0019").contest
    assert contest.end_type == "double_hansoku"


def test_walkover_outcome() -> None:
    contest = parse_fixture("gs_fra2026/03_contests_w12_fu70.json", "gs_fra2026_0002_f_0070_0043").contest
    assert contest.end_type == "fusen_gachi"


@pytest.mark.parametrize(
    ("events", "overrides", "end_type"),
    [
        ([raw_event(1, "1", tags=[KIKEN_GACHI])], {}, "kiken_gachi"),
        ([raw_event(1, "1")], {}, "ippon"),
        ([raw_event(1, "3", tags=[OTHER_WIN])], {}, "score_regulation"),
        ([raw_event(1, "4", is_gs="1")], {}, "score_gs"),
        ([raw_event(1, "3")], {"gs": "1"}, "score_gs"),
        ([raw_event(1, "3")], {"duration": "00:04:01"}, "score_gs"),
        ([raw_event(1, "8"), raw_event(2, "3")], {}, "score_regulation"),
        ([raw_event(1, "1", tags=[FUSEN_GACHI])], {"duration": "00:00:00"}, "fusen_gachi"),
    ],
)
def test_end_type_first_match_wins(events: list[dict[str, Any]], overrides: dict[str, str], end_type: str) -> None:
    assert parsed(raw_contest(events=events, **overrides)).contest.end_type == end_type


def test_null_names_are_empty() -> None:
    contest = parsed(raw_contest(given_name_white=None, family_name_blue=None))
    assert (contest.athletes[0].given_name, contest.athletes[1].family_name) == ("", "")


@pytest.mark.parametrize("field", ["country_short_white", "country_short_blue"])
def test_contest_without_a_country_is_skipped(field: str) -> None:
    assert parse_contest(raw_contest(**{field: None}), COMPETITION) == SkippedContest("missing country")
