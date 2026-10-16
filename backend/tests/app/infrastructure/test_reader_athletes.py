import pytest
from sqlalchemy import Engine

from judogg.app.infrastructure.reader import PostgresDatasetReader


@pytest.fixture(scope="module")
def reader(engine: Engine) -> PostgresDatasetReader:
    return PostgresDatasetReader(engine)


def test_athletes_by_id_and_all(reader: PostgresDatasetReader) -> None:
    some = reader.athletes([900196, 1])
    assert list(some) == [900196]
    assert (some[900196].given_name, some[900196].family_name, some[900196].country_code) == (
        "Meve",
        "KIPOPI",
        "CAN",
    )
    assert len(reader.athletes(None)) == 506


def test_search_on_both_name_orders(reader: PostgresDatasetReader) -> None:
    assert [a.id for a in reader.search_athletes("meve kipo")] == [900196]
    assert [a.id for a in reader.search_athletes("kipopi mev")] == [900196]


def test_search_escapes_like_wildcards(reader: PostgresDatasetReader) -> None:
    assert reader.search_athletes("%") == []
    assert reader.search_athletes("_") == []


def test_rows_of_given_athletes(reader: PostgresDatasetReader) -> None:
    contests = reader.contests_of_athletes([900196])
    assert contests and all(900196 in (c.white_athlete_id, c.blue_athlete_id) for c in contests)
    scores = reader.scores_of_athletes([900196])
    assert scores and all(s.athlete_id == 900196 for s in scores)
    assert reader.contests_of_athletes([]) == [] and reader.scores_of_athletes([]) == []
