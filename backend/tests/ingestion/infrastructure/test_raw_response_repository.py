from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, text

from judogg.ingestion.application.raw_responses import RawResponse
from judogg.ingestion.infrastructure.raw_response_repository import PostgresRawResponseRepository


@pytest.fixture
def repository(engine: Engine) -> Iterator[PostgresRawResponseRepository]:
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE ingestion.raw_response"))
    yield PostgresRawResponseRepository(engine)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE ingestion.raw_response"))


def contests(competition: str, weight: str, payload: object) -> RawResponse:
    params = {"id_competition": competition, "id_weight": weight, "part": "info,score_list,media,events"}
    return RawResponse("contest.find", params, payload)


def test_save_overwrites_the_same_call(repository: PostgresRawResponseRepository) -> None:
    repository.save(RawResponse("competition.get_list", {}, [1]))
    repository.save(RawResponse("competition.get_list", {}, [2]))
    assert repository.get("competition.get_list", {}) == [2]
    assert repository.get("competition.categories_full", {"id_competition": "1"}) is None


def test_contest_payloads_by_competition(repository: PostgresRawResponseRepository) -> None:
    repository.save(contests("20", "1", {"contests": ["a"]}))
    repository.save(contests("10", "1", {"contests": ["b"]}))
    repository.save(contests("10", "2", {"contests": ["c"]}))
    assert repository.contest_competition_ids() == [10, 20]
    assert sorted(p["contests"][0] for p in repository.contest_payloads(10)) == ["b", "c"]
