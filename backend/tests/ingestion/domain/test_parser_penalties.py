import pytest
from ijf_helpers import (
    GUADALAJARA,
    NEW_GROUP_REASON,
    NON_COMBATIVITY,
    make_competition,
    parse_fixture,
    raw_contest,
    raw_event,
)

from judogg.ingestion.domain.model import ParsedContest, Penalty, QualityIssue
from judogg.ingestion.domain.parser import parse_contest


def parsed(**overrides: object) -> ParsedContest:
    result = parse_contest(raw_contest(**overrides), make_competition())
    assert isinstance(result, ParsedContest)
    return result


def test_cancelled_shido_is_not_a_penalty() -> None:
    contest = parse_fixture(GUADALAJARA, "gp_mex2025_0001_m_0066_0030")
    blue = contest.contest.blue_athlete_id
    assert [p.athlete_id for p in contest.penalties].count(blue) == 1


def test_simultaneous_shido_gives_two_rows() -> None:
    contest = parse_fixture(GUADALAJARA, "gp_mex2025_0001_m_0066_0006")
    rows = sorted((p.athlete_id, p.shido_number, p.reason_tag_id) for p in contest.penalties if p.event_id == 645193)
    assert rows == [(900416, 2, 310), (900430, 1, 310)]


def test_hansoku_make_by_shido() -> None:
    contest = parse_fixture(GUADALAJARA, "gp_mex2025_0001_m_0066_0008")
    assert [(p.athlete_id, p.penalty_kind, p.shido_number) for p in contest.penalties] == [
        (900278, "shido", 1),
        (900278, "shido", 2),
        (900257, "shido", 1),
        (900278, "hansoku_shido", 3),
    ]
    assert contest.scores == ()
    assert not [i for i in contest.issues if i.code == "summary_mismatch"]


def test_double_hansoku_gives_two_rows() -> None:
    contest = parse_fixture("gs_fra2026/03_contests_w11_fu63.json", "gs_fra2026_0002_f_0063_0019")
    assert len([p for p in contest.penalties if p.event_id == 693363 and p.penalty_kind == "hansoku_shido"]) == 2


def test_penalty_row_fields() -> None:
    contest = parsed(events=[raw_event(1, "5", actors=[20], tags=[NON_COMBATIVITY], time_sc="61")], penalty_b="1")
    assert contest.penalties == (Penalty(1, 1, contest.contest.dims, 20, "FRA", "shido", 1, 5, False, 2),)
    assert [t.code for t in contest.tags] == ["non_combativity"]


def test_penalty_without_reason_and_reason_with_unknown_group() -> None:
    contest = parsed(
        events=[raw_event(1, "5"), raw_event(2, "5", tags=[NEW_GROUP_REASON], time_sc="20")], penalty_w="2"
    )
    assert [p.reason_tag_id for p in contest.penalties] == [None, 6]
    assert contest.issues == (QualityIssue("new_tag_group", 1, 2, {"id_group": "115"}),)


@pytest.mark.parametrize(
    "code",
    ["gs_fra2026_0001_m_0060_0063", "gs_fra2026_0001_m_0060_0033", "gs_fra2026_0001_m_0060_0035"],
)
def test_the_three_paris_summary_mismatches(code: str) -> None:
    contest = parse_fixture("gs_fra2026/03_contests_w01_mu60.json", code)
    assert [i.code for i in contest.issues] == ["summary_mismatch"]
    assert contest.contest.has_quality_issue is True


def test_summary_mismatch_detail() -> None:
    contest = parsed(events=[raw_event(1, "3")])
    assert contest.issues == (
        QualityIssue("summary_mismatch", 1, None, {"field": "waza_w", "summary": 0, "events": 1}),
    )


def test_null_summary_field_counts_as_zero() -> None:
    assert parsed(ippon_b=None).issues == ()


def test_repeated_competitor_in_one_penalty_counts_once() -> None:
    contest = parsed(events=[raw_event(1, "7", actors=[10, 10])], penalty_w="1", ippon_b="1")
    assert [(p.athlete_id, p.penalty_kind) for p in contest.penalties] == [(10, "hansoku_shido")]
    assert contest.contest.end_type == "hansoku_shido"
