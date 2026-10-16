from collections.abc import Iterator
from decimal import Decimal

import pytest
from ijf_helpers import FIXTURES, SEEDS
from sqlalchemy import Engine, text
from typer.testing import CliRunner

from judogg.db import tables
from judogg.ingestion.application.errors import LoadError
from judogg.ingestion.application.raw_responses import RawResponse
from judogg.ingestion.infrastructure.raw_response_repository import PostgresRawResponseRepository
from judogg.ingestion.interfaces.cli import app, import_files, run_load


@pytest.fixture
def clean_raw(engine: Engine) -> Iterator[None]:
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE ingestion.raw_response"))
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE ingestion.raw_response"))


def scalar(engine: Engine, sql: str) -> object:
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar_one()


def rows(engine: Engine, sql: str) -> list[tuple[object, ...]]:
    with engine.connect() as conn:
        return [tuple(r) for r in conn.execute(text(sql)).all()]


@pytest.mark.usefixtures("clean_raw")
def test_load_the_example_data(engine: Engine) -> None:
    import_files(engine, FIXTURES)
    run_load(engine, SEEDS)
    assert scalar(engine, "SELECT count(*) FROM app.competition") == 715
    assert scalar(engine, "SELECT count(*) FROM app.competition WHERE exclusion_reason IS NOT NULL") == 91
    assert rows(
        engine,
        "SELECT id, level, exclusion_reason, tag_coverage FROM app.competition "
        "WHERE id IN (1439, 2942, 3081, 3131) ORDER BY id",
    ) == [
        (1439, "continental", "no events", None),
        (2942, "continental", "technique tags on 0% of scores", Decimal("0.0000")),
        (3081, "elite", None, Decimal("0.9762")),
        (3131, "elite", None, Decimal("0.9132")),
    ]
    assert rows(engine, "SELECT id, label FROM app.ruleset ORDER BY id") == [
        (2017, "2017"),
        (2018, "2018–2024"),
        (2025, "2025–"),
    ]
    assert scalar(engine, "SELECT count(*) FROM app.contest") == 556
    assert scalar(engine, "SELECT count(*) FROM app.athlete") == 506
    assert rows(engine, "SELECT kind, count(*) FROM app.tag GROUP BY kind ORDER BY kind") == [
        ("shido_reason", 20),
        ("technique", 58),
    ]
    assert scalar(engine, "SELECT count(DISTINCT (event_id, athlete_id)) FROM app.score") == 756
    assert scalar(engine, "SELECT count(*) FROM app.score") == 757
    assert (
        scalar(engine, "SELECT count(DISTINCT (event_id, athlete_id)) FROM app.score WHERE technique_tag_id IS NULL")
        == 63
    )
    assert rows(engine, "SELECT penalty_kind, count(*) FROM app.penalty GROUP BY 1 ORDER BY 1") == [
        ("hansoku_shido", 57),
        ("shido", 910),
    ]
    assert {str(k): v for k, v in rows(engine, "SELECT end_type, count(*) FROM app.contest GROUP BY 1")} == {
        "ippon": 211,
        "score_regulation": 163,
        "score_gs": 77,
        "hansoku_shido": 55,
        "waza_ari_awasete": 39,
        "fusen_gachi": 8,
        "kiken_gachi": 2,
        "double_hansoku": 1,
    }
    assert rows(
        engine, "SELECT code, count(*), count(DISTINCT contest_id) FROM app.data_quality_issue GROUP BY code"
    ) == [("summary_mismatch", 3, 3)]
    assert scalar(engine, "SELECT count(*) FROM app.contest WHERE has_quality_issue") == 3
    assert rows(engine, "SELECT family_name, given_name, country_code FROM app.athlete WHERE id = 900196") == [
        ("KIPOPI", "Meve", "CAN"),
    ]


@pytest.mark.usefixtures("clean_raw")
def test_load_is_idempotent(engine: Engine) -> None:
    snapshot = "SELECT md5(coalesce(string_agg(t::text, ',' ORDER BY t::text), '')) FROM app.{} t"
    names = [table.name for table in tables.APP_TABLES]
    import_files(engine, FIXTURES)
    run_load(engine, SEEDS)
    first = [scalar(engine, snapshot.format(name)) for name in names]
    run_load(engine, SEEDS)
    assert [scalar(engine, snapshot.format(name)) for name in names] == first


@pytest.mark.usefixtures("clean_raw")
def test_a_failing_load_leaves_the_previous_data(engine: Engine) -> None:
    import_files(engine, FIXTURES)
    run_load(engine, SEEDS)
    PostgresRawResponseRepository(engine).save(
        RawResponse("contest.find", {"id_competition": "999999", "id_weight": "1", "part": "x"}, {"contests": []})
    )
    with pytest.raises(LoadError):
        run_load(engine, SEEDS)
    assert scalar(engine, "SELECT count(*) FROM app.contest") == 556


@pytest.mark.usefixtures("clean_raw")
def test_cli_load_without_data_exits_1(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SEEDS_DIR", str(SEEDS))
    result = CliRunner().invoke(app, ["load"])
    assert result.exit_code == 1
    assert "competitions list is not stored" in result.output


@pytest.mark.usefixtures("clean_raw")
def test_cli_load_prints_a_summary(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SEEDS_DIR", str(SEEDS))
    result = CliRunner().invoke(app, ["load", "--files", str(FIXTURES)])
    assert result.exit_code == 0, result.output
    assert "Imported 22 files" in result.output
    assert "contest: 556" in result.output
    assert "Odivelas European Open 2017: no events" in result.output
    assert "Contests skipped: none" in result.output


def test_cli_without_database_url_exits_1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    result = CliRunner().invoke(app, ["load"])
    assert result.exit_code == 1
    assert "Configuration error" in result.output and "database_url" in result.output


def test_cli_load_from_a_missing_directory_exits_2() -> None:
    result = CliRunner().invoke(app, ["load", "--files", "/no/such/directory"])
    assert result.exit_code == 2
