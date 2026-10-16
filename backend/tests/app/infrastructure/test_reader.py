import pytest
from sqlalchemy import Engine

from judogg.app.application.filters import resolve_filters
from judogg.app.infrastructure.reader import PostgresDatasetReader


@pytest.fixture(scope="module")
def reader(engine: Engine) -> PostgresDatasetReader:
    return PostgresDatasetReader(engine)


def test_catalogue(reader: PostgresDatasetReader) -> None:
    catalogue = reader.catalogue()
    assert [w.code for w in catalogue.weights][:2] == ["m-60", "m-66"]
    assert [(r.id, r.contests) for r in catalogue.rulesets] == [(2017, 0), (2018, 0), (2025, 556)]
    assert len(catalogue.tags) == 78
    assert len(catalogue.competitions) == 715
    paris = catalogue.competitions[3131]
    assert (paris.level, paris.tag_coverage, paris.exclusion_reason) == ("elite", 0.9132, None)


def test_every_row(reader: PostgresDatasetReader) -> None:
    assert (len(reader.scores(None)), len(reader.contests(None)), len(reader.penalties(None))) == (757, 556, 967)
    counts = reader.table_counts()
    assert (counts.athletes, counts.penalties) == (506, 967)
    assert [i.code for i in reader.quality_issues()] == ["summary_mismatch"] * 3


def test_filtered_rows_match_the_filters(reader: PostgresDatasetReader) -> None:
    catalogue = reader.catalogue()
    men_73 = resolve_filters({"gender": "m", "weight": "m-73", "country": "JPN", "side": "left"}, catalogue)
    scores = reader.scores(men_73)
    assert scores and {(s.weight, s.athlete_country, s.direction) for s in scores} == {("m-73", "JPN", "left")}
    contests = reader.contests(men_73)
    assert contests and all("JPN" in (c.white_country_code, c.blue_country_code) for c in contests)
    assert {p.weight for p in reader.penalties(men_73)} == {"m-73"}
    standing = resolve_filters({"domain": "standing"}, catalogue)
    assert all(s.technique_tag_id is not None for s in reader.scores(standing))


def test_a_ruleset_without_contests_gives_no_rows(reader: PostgresDatasetReader) -> None:
    empty = resolve_filters({"ruleset": "2018"}, reader.catalogue())
    assert (reader.scores(empty), reader.contests(empty), reader.penalties(empty)) == ([], [], [])


def test_reader_releases_its_connections(engine: Engine, reader: PostgresDatasetReader) -> None:
    reader.catalogue()
    reader.scores(None)
    assert engine.pool.checkedout() == 0  # type: ignore[attr-defined]
