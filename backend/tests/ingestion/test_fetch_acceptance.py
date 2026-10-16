from collections.abc import Iterator
from datetime import date

import pytest
from ijf_helpers import FIXTURES, SEEDS
from ingestion_fakes import FakeIjfClient, FixedClock
from sqlalchemy import Engine, text
from typer.testing import CliRunner

from judogg.ingestion.domain.selection import Selection
from judogg.ingestion.infrastructure.ijf_files import read_ijf_files
from judogg.ingestion.interfaces import cli
from judogg.ingestion.interfaces.cli import app, run_fetch, run_load


@pytest.fixture
def clean_raw(engine: Engine) -> Iterator[None]:
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE ingestion.raw_response"))
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE ingestion.raw_response"))


@pytest.fixture
def fake_ijf(monkeypatch: pytest.MonkeyPatch) -> None:
    """The command never reaches the IJF in tests: it gets the example files instead."""
    monkeypatch.setattr(cli, "ijf_client", lambda settings, delay: FakeIjfClient(read_ijf_files(FIXTURES)))
    monkeypatch.setenv("SEEDS_DIR", str(SEEDS))


def scalar(engine: Engine, sql: str) -> object:
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar_one()


@pytest.mark.usefixtures("clean_raw")
def test_fetch_then_load_a_competition(engine: Engine) -> None:
    progress: list[str] = []
    summary = run_fetch(
        engine,
        FakeIjfClient(read_ijf_files(FIXTURES)),
        FixedClock(date(2026, 10, 13)),
        SEEDS,
        Selection(competition_ids=(3131,)),
        force=False,
        progress=progress.append,
    )
    assert (summary.downloaded, summary.failed) == (16, ())
    assert scalar(engine, "SELECT count(*) FROM ingestion.raw_response") == 16
    run_load(engine, SEEDS)
    assert scalar(engine, "SELECT count(*) FROM app.contest WHERE competition_id = 3131") == 528


@pytest.mark.usefixtures("clean_raw", "fake_ijf")
def test_cli_fetch_and_load(engine: Engine) -> None:
    result = CliRunner().invoke(app, ["fetch", "--competition", "3131", "--load"])
    assert result.exit_code == 0, result.output
    assert "3131 Paris Grand Slam 2026: 15 downloaded, 0 skipped, 0 failed" in result.output
    assert "Calls: 16 downloaded, 0 skipped, 0 failed" in result.output
    assert "contest: 528" in result.output


@pytest.mark.usefixtures("clean_raw", "fake_ijf")
def test_cli_fetch_with_failed_calls_exits_1_and_does_not_load(engine: Engine) -> None:
    contests_before = scalar(engine, "SELECT count(*) FROM app.contest")
    result = CliRunner().invoke(app, ["fetch", "--competition", "3081", "--load"])
    assert result.exit_code == 1
    assert "Calls: 3 downloaded, 0 skipped, 13 failed" in result.output
    assert "Failed calls:" in result.output and "Load skipped" in result.output
    assert scalar(engine, "SELECT count(*) FROM app.contest") == contests_before


@pytest.mark.usefixtures("fake_ijf")
@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["fetch"], "at least one of --year, --competition, --recent-months"),
        (["fetch", "--year", "2016"], "before 2017"),
        (["fetch", "--recent-months", "0"], "recent-months"),
    ],
)
def test_cli_fetch_bad_options_exit_2(args: list[str], message: str) -> None:
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 2
    assert message in result.output


@pytest.mark.usefixtures("clean_raw", "fake_ijf")
def test_cli_fetch_unknown_competition_exits_1() -> None:
    result = CliRunner().invoke(app, ["fetch", "--competition", "999999"])
    assert result.exit_code == 1
    assert "Fetch failed: competition 999999 is not in the IJF competitions list" in result.output
