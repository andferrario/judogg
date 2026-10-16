import copy

import pytest
from ijf_helpers import FIXTURES, exclusion_rules
from ingestion_fakes import FakeDataset, FakeRawResponses

from judogg.ingestion.application.errors import LoadError
from judogg.ingestion.application.raw_responses import RawResponse
from judogg.ingestion.application.rebuild_dataset import RebuildDataset
from judogg.ingestion.infrastructure.ijf_files import read_ijf_files

FIND = {"id_weight": "1", "part": "info,score_list,media,events"}


def run(raw: FakeRawResponses) -> tuple[FakeDataset, RebuildDataset]:
    dataset = FakeDataset()
    return dataset, RebuildDataset(raw, dataset, exclusion_rules())


def test_rebuild_from_the_example_files() -> None:
    dataset, use_case = run(FakeRawResponses(read_ijf_files(FIXTURES)))
    summary = use_case.execute()
    writer = dataset.writer
    assert writer is not None
    assert (len(writer.rulesets), len(writer.competitions), len(writer.contests)) == (3, 715, 556)
    assert summary.included == 2
    assert sorted(summary.excluded) == [
        ("Conegliano European Open 2025", "technique tags on 0% of scores"),
        ("Odivelas European Open 2017", "no events"),
    ]
    assert summary.issues == {"summary_mismatch": 3}
    assert (summary.skipped, summary.without_contests) == ({}, ())
    # chronological: Guadalajara (October 2025) before Paris (February 2026)
    assert writer.contests[0].contest.dims.competition_id == 3081
    assert writer.contests[-1].contest.dims.competition_id == 3131


def test_missing_competition_list_fails() -> None:
    _, use_case = run(FakeRawResponses())
    with pytest.raises(LoadError, match="competitions list"):
        use_case.execute()


def test_contest_data_of_an_unlisted_competition_fails() -> None:
    responses = [
        *read_ijf_files(FIXTURES),
        RawResponse("contest.find", {"id_competition": "999999", **FIND}, {"contests": []}),
    ]
    dataset, use_case = run(FakeRawResponses(responses))
    with pytest.raises(LoadError, match="999999"):
        use_case.execute()
    assert dataset.writer is None


def test_duplicate_contest_fails() -> None:
    responses = read_ijf_files(FIXTURES)
    guadalajara = next(r for r in responses if r.competition_id == 3081 and r.endpoint == "contest.find")
    duplicate = RawResponse(
        "contest.find", {**guadalajara.params, "id_weight": "99"}, copy.deepcopy(guadalajara.payload)
    )
    _, use_case = run(FakeRawResponses([*responses, duplicate]))
    with pytest.raises(LoadError, match="appears twice"):
        use_case.execute()


def test_empty_contest_payloads_are_ignored() -> None:
    responses = [
        *read_ijf_files(FIXTURES),
        RawResponse("contest.find", {"id_competition": "3081", "id_weight": "50", "part": FIND["part"]}, []),
        RawResponse(
            "contest.find", {"id_competition": "3081", "id_weight": "51", "part": FIND["part"]}, {"contests": []}
        ),
    ]
    dataset, use_case = run(FakeRawResponses(responses))
    use_case.execute()
    assert dataset.writer is not None and len(dataset.writer.contests) == 556


def test_contest_data_before_2017_and_of_excluded_competitions_is_ignored() -> None:
    listing = read_ijf_files(FIXTURES)[0]
    old = next(c for c in listing.payload if int(c["comp_year"]) < 2017)
    kata = next(c for c in listing.payload if c["rank_name"] == "Kata Tournament" and int(c["comp_year"]) >= 2017)
    responses = [listing] + [
        RawResponse("contest.find", {"id_competition": c["id_competition"], **FIND}, {"contests": [{"broken": 1}]})
        for c in (old, kata)
    ]
    dataset, use_case = run(FakeRawResponses(responses))
    use_case.execute()
    assert dataset.writer is not None and dataset.writer.contests == []


def test_unreadable_contest_fails_naming_the_competition_and_the_contest() -> None:
    responses = read_ijf_files(FIXTURES)
    guadalajara = next(r for r in responses if r.competition_id == 3081 and r.endpoint == "contest.find")
    payload = copy.deepcopy(guadalajara.payload)
    payload["contests"][3]["id_person_white"] = None
    code = payload["contests"][3]["contest_code_long"]
    broken = RawResponse("contest.find", guadalajara.params, payload)
    dataset, use_case = run(FakeRawResponses([*responses, broken]))
    with pytest.raises(LoadError, match=rf"competition 3081 .*contest {code}"):
        use_case.execute()
    assert dataset.writer is None


@pytest.mark.parametrize(
    ("year", "field", "value"),
    [
        ("2026", "max_shido", None),  # unreadable entry
        ("2018", "has_yuko", "1"),  # a yuko ruleset starting in 2018 collides with the 2018 ruleset id
    ],
)
def test_unreadable_competitions_list_fails_with_a_load_error(year: str, field: str, value: str | None) -> None:
    entries = copy.deepcopy(read_ijf_files(FIXTURES)[0].payload)
    next(c for c in entries if c["comp_year"] == year)[field] = value
    _, use_case = run(FakeRawResponses([RawResponse("competition.get_list", {}, entries)]))
    with pytest.raises(LoadError, match="competitions list"):
        use_case.execute()


def test_competition_whose_contests_are_all_skipped_is_reported() -> None:
    responses = read_ijf_files(FIXTURES)
    guadalajara = next(r for r in responses if r.competition_id == 3081 and r.endpoint == "contest.find")
    payload = copy.deepcopy(guadalajara.payload)
    for contest in payload["contests"]:
        contest["age"] = "Senior"
    responses = [r for r in responses if r is not guadalajara] + [
        RawResponse("contest.find", guadalajara.params, payload)
    ]
    _, use_case = run(FakeRawResponses(responses))
    summary = use_case.execute()
    assert summary.skipped == {"age Senior": 28}
    assert summary.without_contests == ("Guadalajara Grand Prix 2025",)
    assert summary.included == 1


def test_summary_counts_exclusions_per_reason_with_the_name_and_rank_rules() -> None:
    responses = read_ijf_files(FIXTURES)
    kata = next(c for c in responses[0].payload if c["rank_name"] == "Kata Tournament" and int(c["comp_year"]) >= 2017)
    responses.append(RawResponse("contest.find", {"id_competition": kata["id_competition"], **FIND}, {"contests": []}))
    _, use_case = run(FakeRawResponses(responses))
    summary = use_case.execute()
    assert summary.excluded_per_reason == {
        "rank_name Kata Tournament": 1,
        "no events": 1,
        "technique tags on less than 70% of scores": 1,
    }
    assert (kata["name"], "rank_name Kata Tournament") in summary.excluded
    assert summary.included == 2


def test_summary_lists_the_unknown_tag_groups() -> None:
    responses = read_ijf_files(FIXTURES)
    guadalajara = next(r for r in responses if r.competition_id == 3081 and r.endpoint == "contest.find")
    payload = copy.deepcopy(guadalajara.payload)
    tags = (t for c in payload["contests"] for e in c.get("events") or [] for t in e.get("tags") or [])
    next(t for t in tags if "28" in str(t["id_groups"]).split(","))["id_group"] = "32"
    responses = [r for r in responses if r is not guadalajara] + [
        RawResponse("contest.find", guadalajara.params, payload)
    ]
    _, use_case = run(FakeRawResponses(responses))
    assert use_case.execute().new_tag_groups == ("32",)


@pytest.mark.parametrize("listing", [{"error": "maintenance"}, [{"name": "no id"}]])
def test_a_stored_list_that_is_not_a_competitions_list_fails_with_a_load_error(listing: object) -> None:
    _, use_case = run(FakeRawResponses([RawResponse("competition.get_list", {}, listing)]))
    with pytest.raises(LoadError, match="competitions list"):
        use_case.execute()
