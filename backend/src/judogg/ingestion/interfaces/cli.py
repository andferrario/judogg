"""Composition root of the ingestion: the only module that instantiates infrastructure classes."""

from collections.abc import Callable
from contextlib import closing
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from sqlalchemy import Engine, create_engine

from judogg.ingestion.application.errors import FetchError, LoadError
from judogg.ingestion.application.fetch_competitions import FetchCompetitions, FetchSummary
from judogg.ingestion.application.import_raw_files import ImportRawFiles
from judogg.ingestion.application.ports import Clock, IjfClient
from judogg.ingestion.application.rebuild_dataset import LoadSummary, RebuildDataset
from judogg.ingestion.domain.selection import InvalidSelection, Selection, parse_years
from judogg.ingestion.infrastructure.clock import SystemClock
from judogg.ingestion.infrastructure.dataset_repository import PostgresDatasetRepository
from judogg.ingestion.infrastructure.ijf_client import HttpIjfClient
from judogg.ingestion.infrastructure.ijf_files import read_ijf_files
from judogg.ingestion.infrastructure.raw_response_repository import PostgresRawResponseRepository
from judogg.ingestion.infrastructure.seeds import load_exclusion_rules
from judogg.ingestion.infrastructure.settings import IngestionSettings

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.callback()
def main() -> None:
    """Judogg ingestion: from the IJF data to the app tables."""


def settings_or_exit() -> IngestionSettings:
    try:
        return IngestionSettings()
    except ValidationError as error:
        typer.echo(f"Configuration error: {error}", err=True)
        raise typer.Exit(1) from error


@app.command()
def load(
    files: Annotated[
        Path | None,
        typer.Option(exists=True, file_okay=False, help="Import the example IJF files of this directory first."),
    ] = None,
) -> None:
    """Rebuild all app tables from the stored raw IJF responses, in one transaction."""
    settings = settings_or_exit()
    engine = create_engine(settings.database_url)
    try:
        if files is not None:
            typer.echo(f"Imported {import_files(engine, files)} files")
        summary = run_load(engine, settings.seeds_dir)
    except LoadError as error:
        typer.echo(f"Load failed: {error}", err=True)
        raise typer.Exit(1) from error
    finally:
        engine.dispose()
    typer.echo(format_summary(summary))


def import_files(engine: Engine, files: Path) -> int:
    return ImportRawFiles(PostgresRawResponseRepository(engine), read_ijf_files).execute(files)


def run_load(engine: Engine, seeds: Path) -> LoadSummary:
    rules = load_exclusion_rules(seeds / "exclusions.yaml")
    return RebuildDataset(PostgresRawResponseRepository(engine), PostgresDatasetRepository(engine), rules).execute()


@app.command()
def fetch(
    year: Annotated[str | None, typer.Option(help="A year, a comma list (2025,2026) or a range (2020-2026).")] = None,
    competition: Annotated[
        list[int] | None, typer.Option(help="A competition id (id_competition); repeatable.")
    ] = None,
    recent_months: Annotated[
        int | None, typer.Option(min=1, help="Competitions started in the last N months, always downloaded again.")
    ] = None,
    elite_only: Annotated[
        bool, typer.Option("--elite-only", help="Download only elite competitions (Grand Slam, Grand Prix, etc.).")
    ] = False,
    force: Annotated[bool, typer.Option(help="Download again the calls already stored.")] = False,
    delay: Annotated[float | None, typer.Option(min=0, help="Seconds between calls (default: FETCH_DELAY_S).")] = None,
    then_load: Annotated[bool, typer.Option("--load", help="Run load at the end, only if no call failed.")] = False,
) -> None:
    """Download IJF competitions into the raw responses; resumable by running the same command again."""
    selection = Selection(_years(year), tuple(competition or ()), recent_months, elite_only=elite_only)
    if selection.is_empty:
        raise typer.BadParameter("choose at least one of --year, --competition, --recent-months")
    settings = settings_or_exit()
    engine = create_engine(settings.database_url)
    try:
        with closing(ijf_client(settings, delay)) as client:
            summary = run_fetch(
                engine, client, SystemClock(), settings.seeds_dir, selection, force=force, progress=typer.echo
            )
        typer.echo(format_fetch_summary(summary))
        if summary.failed:
            if then_load:
                typer.echo("Load skipped: some calls failed. Run the same command again to retry them.", err=True)
            raise typer.Exit(1)
        if then_load:
            typer.echo(format_summary(run_load(engine, settings.seeds_dir)))
    except FetchError as error:
        typer.echo(f"Fetch failed: {error}", err=True)
        raise typer.Exit(1) from error
    except LoadError as error:
        typer.echo(f"Load failed: {error}", err=True)
        raise typer.Exit(1) from error
    finally:
        engine.dispose()


def ijf_client(settings: IngestionSettings, delay: float | None) -> HttpIjfClient:
    return HttpIjfClient(
        delay_s=settings.fetch_delay_s if delay is None else delay,
        timeout_s=settings.fetch_timeout_s,
        retries=settings.fetch_retries,
    )


def run_fetch(
    engine: Engine,
    client: IjfClient,
    clock: Clock,
    seeds: Path,
    selection: Selection,
    *,
    force: bool,
    progress: Callable[[str], None],
) -> FetchSummary:
    rules = load_exclusion_rules(seeds / "exclusions.yaml")
    use_case = FetchCompetitions(client, PostgresRawResponseRepository(engine), clock, rules, progress)
    return use_case.execute(selection, force=force)


def format_fetch_summary(summary: FetchSummary) -> str:
    lines = [
        f"Competitions: {summary.competitions}",
        f"Calls: {summary.downloaded} downloaded, {summary.skipped} skipped, {len(summary.failed)} failed",
    ]
    if summary.failed:
        lines.append("Failed calls:")
        lines += [f"  {call}" for call in summary.failed]
    return "\n".join(lines)


def _years(text: str | None) -> frozenset[int]:
    if text is None:
        return frozenset()
    try:
        return parse_years(text)
    except InvalidSelection as error:
        raise typer.BadParameter(str(error), param_hint="--year") from error


def format_summary(summary: LoadSummary) -> str:
    lines = ["Rows per table:"]
    lines += [f"  {table}: {count}" for table, count in summary.table_counts.items()]
    lines.append(f"Competitions with contest data: {summary.included} included, {len(summary.excluded)} excluded")
    lines += [f"  {reason}: {count}" for reason, count in sorted(summary.excluded_per_reason.items())]
    if summary.excluded:
        lines.append("Excluded competitions:")
        lines += [f"  {name}: {reason}" for name, reason in summary.excluded]
    if summary.without_contests:
        lines.append(f"Competitions with contest data but no written contest: {len(summary.without_contests)}")
        lines += [f"  {name}" for name in summary.without_contests]
    lines.append("Contests skipped:" if summary.skipped else "Contests skipped: none")
    lines += [f"  {reason}: {count}" for reason, count in sorted(summary.skipped.items())]
    lines.append("Quality issues:" if summary.issues else "Quality issues: none")
    lines += [f"  {code}: {count}" for code, count in sorted(summary.issues.items())]
    lines.append(f"Unknown tag groups: {', '.join(summary.new_tag_groups) or 'none'}")
    return "\n".join(lines)
