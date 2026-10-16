from decimal import Decimal
from typing import Any

from ijf_helpers import SEOI_NAGE, fixture_competitions, load_fixture, make_competition, raw_contest, raw_event

from judogg.ingestion.domain.inclusion import decide_inclusion, reason_kind
from judogg.ingestion.domain.model import Inclusion, ParsedContest, QualityIssue
from judogg.ingestion.domain.parser import parse_contest


def parse_all(relative: str) -> list[ParsedContest]:
    contests: list[dict[str, Any]] = load_fixture(relative)["contests"]
    competition = fixture_competitions()[int(contests[0]["id_competition"])]
    results = [parse_contest(raw, competition) for raw in contests]
    return sorted((r for r in results if isinstance(r, ParsedContest)), key=lambda p: p.contest.id)


def contest(fight: str, *events: dict[str, Any], **summary: str) -> ParsedContest:
    result = parse_contest(raw_contest(id_fight=fight, events=list(events), **summary), make_competition())
    assert isinstance(result, ParsedContest)
    return result


def test_competition_without_events_is_excluded() -> None:
    contests = parse_all("minor/03_contests_1439_w03_mu73.json")
    assert len(contests) == 41
    assert decide_inclusion(contests) == Inclusion("no events", None, (), ())


def test_competition_without_technique_tags_is_excluded() -> None:
    inclusion = decide_inclusion(parse_all("minor/03_contests_2942_w03_mu73.json"))
    assert (inclusion.exclusion_reason, inclusion.tag_coverage) == ("technique tags on 0% of scores", Decimal("0.0000"))
    assert (inclusion.contests, inclusion.issues) == ((), ())


def test_tagged_competition_is_included() -> None:
    contests = parse_all("03_category_contests_with_events.json")
    inclusion = decide_inclusion(contests)
    assert (inclusion.exclusion_reason, inclusion.tag_coverage) == (None, Decimal("0.9762"))
    assert inclusion.contests == tuple(contests)


def test_contest_without_events_in_an_included_competition_is_skipped() -> None:
    tagged = contest("1", raw_event(1, "3", tags=[SEOI_NAGE]), waza_w="1")
    empty = contest("2")
    inclusion = decide_inclusion([tagged, empty])
    assert inclusion == Inclusion(None, Decimal("1.0000"), (tagged,), (QualityIssue("no_events", 2, None, {}),))


def test_threshold_and_rounding() -> None:
    tagged = [contest(str(i), raw_event(i, "3", tags=[SEOI_NAGE]), waza_w="1") for i in range(1, 8)]
    untagged = [contest(str(i), raw_event(i, "3"), waza_w="1") for i in range(8, 11)]
    assert decide_inclusion(tagged + untagged).exclusion_reason is None  # 7/10 = 0.7 is enough
    inclusion = decide_inclusion(tagged[:6] + untagged)  # 6/9 = 0.6667
    assert (inclusion.exclusion_reason, inclusion.tag_coverage) == (
        "technique tags on 67% of scores",
        Decimal("0.6667"),
    )


def test_competition_with_events_but_no_scores_is_included() -> None:
    shido_only = contest("1", raw_event(1, "5"), penalty_w="1")
    assert decide_inclusion([shido_only]) == Inclusion(None, None, (shido_only,), ())


def test_competition_without_written_contests_is_not_excluded() -> None:
    assert decide_inclusion([]) == Inclusion(None, None, (), ())


def test_reason_kind_groups_the_coverage_reasons() -> None:
    assert reason_kind(Inclusion("technique tags on 63% of scores", Decimal("0.63"), (), ())) == (
        "technique tags on less than 70% of scores"
    )
    assert reason_kind(Inclusion("no events", None, (), ())) == "no events"
    assert reason_kind(Inclusion(None, Decimal("0.9"), (), ())) is None
