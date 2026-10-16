from datetime import date

import pytest
from ijf_helpers import FIXTURES, exclusion_rules
from ingestion_fakes import FakeIjfClient, FakeRawResponses, FixedClock

from judogg.ingestion.application.errors import FetchError
from judogg.ingestion.application.fetch_competitions import FetchCompetitions, FetchSummary
from judogg.ingestion.application.raw_responses import CONTEST_PARTS, RawResponse
from judogg.ingestion.domain.selection import Selection
from judogg.ingestion.infrastructure.ijf_files import read_ijf_files

PARIS = Selection(competition_ids=(3131,))
TODAY = date(2026, 10, 13)


def contests_call(weight: str) -> tuple[str, dict[str, str]]:
    return "contest.find", {"id_competition": "3131", "id_weight": weight, "part": CONTEST_PARTS}


class Run:
    def __init__(self, client: FakeIjfClient, raw: FakeRawResponses | None = None) -> None:
        self.client = client
        self.raw = raw or FakeRawResponses()
        self.progress: list[str] = []

    def fetch(self, selection: Selection = PARIS, force: bool = False) -> FetchSummary:
        use_case = FetchCompetitions(self.client, self.raw, FixedClock(TODAY), exclusion_rules(), self.progress.append)
        return use_case.execute(selection, force=force)


def ijf(**kwargs: object) -> FakeIjfClient:
    return FakeIjfClient(read_ijf_files(FIXTURES), **kwargs)  # type: ignore[arg-type]


def test_a_competition_is_its_categories_and_one_call_per_category() -> None:
    run = Run(ijf())
    assert run.fetch() == FetchSummary(competitions=1, downloaded=16, skipped=0, failed=())
    assert run.client.calls[:2] == [
        ("competition.get_list", {}),
        ("competition.categories_full", {"id_competition": "3131"}),
    ]
    assert run.client.calls[2:] == [contests_call(str(w)) for w in range(1, 15)]
    assert len(run.raw.rows) == 16
    assert run.progress == ["3131 Paris Grand Slam 2026: 15 downloaded, 0 skipped, 0 failed"]


def test_a_second_run_only_downloads_the_list() -> None:
    run = Run(ijf())
    run.fetch()
    run.client.calls.clear()
    assert run.fetch() == FetchSummary(competitions=1, downloaded=1, skipped=15, failed=())
    assert run.client.calls == [("competition.get_list", {})]


def test_force_downloads_everything_again() -> None:
    run = Run(ijf())
    run.fetch()
    assert run.fetch(force=True).downloaded == 16


def test_a_failed_call_is_reported_and_the_download_goes_on() -> None:
    run = Run(ijf(failing=[contests_call("1")]))
    summary = run.fetch()
    assert (summary.downloaded, len(summary.failed)) == (15, 1)
    assert (
        "contest.find" in summary.failed[0]
        and "'id_weight': '1'" in summary.failed[0]
        and "HTTP 404" in summary.failed[0]
    )
    assert ("contest.find", contests_call("1")[1]) not in [(r.endpoint, dict(r.params)) for r in run.raw.rows.values()]
    assert run.progress == ["3131 Paris Grand Slam 2026: 14 downloaded, 0 skipped, 1 failed"]


def test_a_failed_categories_call_skips_the_competition() -> None:
    run = Run(ijf(failing=[("competition.categories_full", {"id_competition": "3131"})]))
    summary = run.fetch()
    assert (summary.downloaded, len(summary.failed)) == (1, 1)
    assert len(run.client.calls) == 2


def test_failed_competitions_list_ends_the_download() -> None:
    run = Run(FakeIjfClient([]))
    assert run.fetch() == FetchSummary(
        competitions=0, downloaded=0, skipped=0, failed=("competition.get_list {}: HTTP 404",)
    )
    assert run.client.calls == [("competition.get_list", {})]


def test_unknown_competition_is_a_fetch_error() -> None:
    with pytest.raises(FetchError, match="competition 999999 is not in the IJF competitions list"):
        Run(ijf()).fetch(Selection(competition_ids=(999999,)))


def test_empty_categories_make_no_contest_call() -> None:
    responses = [r for r in read_ijf_files(FIXTURES) if r.endpoint != "competition.categories_full"]
    responses.append(RawResponse("competition.categories_full", {"id_competition": "3131"}, []))
    run = Run(FakeIjfClient(responses))
    assert run.fetch() == FetchSummary(competitions=1, downloaded=2, skipped=0, failed=())


def test_recent_competitions_are_downloaded_again() -> None:
    responses = read_ijf_files(FIXTURES)
    listing = next(r for r in responses if r.endpoint == "competition.get_list")
    paris_only = RawResponse(
        listing.endpoint, listing.params, [e for e in listing.payload if e["id_competition"] == "3131"]
    )
    served = [paris_only, *(r for r in responses if r is not listing)]
    run = Run(FakeIjfClient(served), FakeRawResponses(served))
    assert run.fetch(Selection(recent_months=12)) == FetchSummary(competitions=1, downloaded=16, skipped=0, failed=())


@pytest.mark.parametrize("answer", [{"error": "maintenance"}, "maintenance", [{"name": "no id"}]])
def test_an_answer_that_is_not_a_competitions_list_is_a_failed_call_and_is_not_stored(answer: object) -> None:
    responses = read_ijf_files(FIXTURES)
    stored = FakeRawResponses(responses)
    good_list = stored.get("competition.get_list", {})
    served = [
        RawResponse("competition.get_list", {}, answer),
        *(r for r in responses if r.endpoint != "competition.get_list"),
    ]
    run = Run(FakeIjfClient(served), stored)
    summary = run.fetch()
    assert summary.failed == ("competition.get_list {}: the answer is not a competitions list",)
    assert run.raw.get("competition.get_list", {}) == good_list
