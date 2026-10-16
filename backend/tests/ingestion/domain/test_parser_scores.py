from ijf_helpers import (
    CANCEL_WAZA_ARI,
    FUSEN_GACHI,
    GUADALAJARA,
    KESA_GATAME,
    LEFT,
    NEW_GROUP_TECHNIQUE,
    OSAEKOMI,
    OTHER_WIN,
    RIGHT,
    SEOI_NAGE,
    UCHI_MATA,
    make_competition,
    parse_fixture,
    raw_contest,
    raw_event,
)

from judogg.ingestion.domain.model import ParsedContest, QualityIssue, Score
from judogg.ingestion.domain.parser import parse_contest


def parsed(**overrides: object) -> ParsedContest:
    result = parse_contest(raw_contest(**overrides), make_competition())
    assert isinstance(result, ParsedContest)
    return result


def score_of(contest: ParsedContest, event_id: int) -> Score:
    return next(s for s in contest.scores if s.event_id == event_id)


def guadalajara_score(code: str, event_id: int) -> Score:
    return score_of(parse_fixture(GUADALAJARA, code), event_id)


def test_the_event_type_is_the_final_score() -> None:
    upgraded = guadalajara_score("gp_mex2025_0001_m_0066_0025", 645414)  # type 1 + "Cancel Waza-ari"
    assert (upgraded.score_value, upgraded.technique_tag_id, upgraded.direction) == ("ippon", 274, "left")
    changed = guadalajara_score("gp_mex2025_0001_m_0066_0022", 645263)  # type 3 + "Cancel Yuko"
    assert (changed.score_value, changed.direction) == ("waza_ari", "right")


def test_awasete_is_a_waza_ari() -> None:
    score = guadalajara_score("gp_mex2025_0001_m_0066_0021", 645251)
    assert (score.score_value, score.is_awasete, score.technique_tag_id, score.time_bin) == ("waza_ari", True, 218, 7)


def test_untagged_score_has_no_technique() -> None:
    score = guadalajara_score("gp_mex2025_0001_m_0066_0035", 645564)  # the final, won by an untagged ippon
    assert (score.technique_tag_id, score.technique_domain, score.direction) == (None, "unknown", "unknown")
    assert (score.is_gs, score.time_bin) == (True, 8)


def test_golden_score_comes_from_is_gs_only() -> None:
    score = guadalajara_score("gp_mex2025_0001_m_0066_0027", 645382)
    assert (score.is_gs, score.time_bin) == (False, 7)


def test_score_row_fields() -> None:
    contest = parsed(events=[raw_event(1, "3", actors=[20], tags=[SEOI_NAGE, RIGHT], time_sc="95")])
    assert contest.scores == (
        Score(1, 1, contest.contest.dims, 20, "FRA", 10, "waza_ari", False, 1, "standing", "right", False, 3),
    )
    assert [t.code for t in contest.tags] == ["seoi_nage"]


def test_time_bins_cap_at_7_in_regulation() -> None:
    contest = parsed(events=[raw_event(1, "4", time_sc="0"), raw_event(2, "4", time_sc="239.9")])
    assert [s.time_bin for s in contest.scores] == [0, 7]


def test_combination_gives_one_row_per_technique() -> None:
    contest = parsed(events=[raw_event(1, "3", tags=[SEOI_NAGE, UCHI_MATA, LEFT])])
    assert [(s.event_id, s.technique_tag_id) for s in contest.scores] == [(1, 1), (1, 2)]


def test_ground_technique_and_context_tags() -> None:
    contest = parsed(events=[raw_event(1, "1", tags=[KESA_GATAME, OSAEKOMI, CANCEL_WAZA_ARI])])
    assert contest.scores[0].technique_domain == "ground"
    assert [t.code for t in contest.tags] == ["kesa_gatame"]


def test_walkover_gives_no_score_row() -> None:
    contest = parsed(events=[raw_event(1, "1", tags=[FUSEN_GACHI])])
    assert contest.scores == ()


def test_unknown_win_type_is_an_issue_and_no_score() -> None:
    contest = parsed(events=[raw_event(1, "1", tags=[OTHER_WIN])])
    assert contest.scores == ()
    assert QualityIssue("new_tag_group", 1, 1, {"id_group": "121", "code_short": "hantei"}) in contest.issues


def test_technique_with_unknown_group_is_stored_with_an_issue() -> None:
    contest = parsed(events=[raw_event(1, "3", tags=[NEW_GROUP_TECHNIQUE])], waza_w="1")
    assert contest.scores[0].technique_domain == "unknown"
    assert contest.issues == (QualityIssue("new_tag_group", 1, 1, {"id_group": "32"}),)
    assert contest.contest.has_quality_issue is False


def test_unknown_event_type_is_ignored_with_an_issue() -> None:
    contest = parsed(events=[raw_event(1, "6")])
    assert (contest.scores, contest.penalties) == ((), ())
    assert contest.issues == (QualityIssue("unknown_event_type", 1, 1, {"type": "6"}),)
    assert contest.contest.has_quality_issue is True


def test_actor_outside_the_contest_is_ignored_with_an_issue() -> None:
    event = raw_event(1, "3", actors=[10, 99])
    event["actors"].append({"actor_type": "referee", "id_person": "500"})
    contest = parsed(events=[event], waza_w="1")
    assert [s.athlete_id for s in contest.scores] == [10]
    assert contest.issues == (QualityIssue("unknown_actor", 1, 1, {"id_person": 99}),)


def test_no_score_events_are_never_scores() -> None:
    contest = parsed(events=[raw_event(1, "8", tags=[SEOI_NAGE, CANCEL_WAZA_ARI])])
    assert (contest.scores, contest.tags) == ((), ())


def test_repeated_technique_tag_in_one_event_gives_one_row() -> None:
    contest = parsed(events=[raw_event(1, "3", tags=[SEOI_NAGE, SEOI_NAGE, RIGHT])], waza_w="1")
    assert [(s.event_id, s.technique_tag_id) for s in contest.scores] == [(1, 1)]


def test_repeated_competitor_in_one_event_scores_once() -> None:
    contest = parsed(events=[raw_event(1, "3", actors=[10, 10], tags=[SEOI_NAGE])], waza_w="1")
    assert [s.athlete_id for s in contest.scores] == [10]
    assert contest.issues == ()


def test_negative_clock_time_falls_in_the_first_bin() -> None:
    contest = parsed(events=[raw_event(1, "4", time_sc="-3")], yuko_w="1")
    assert contest.scores[0].time_bin == 0
