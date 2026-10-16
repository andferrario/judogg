from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import asdict
from typing import Any

from sqlalchemy import Connection, Engine, Table, func, select, text, update
from sqlalchemy.dialects.postgresql import insert

from judogg.db import tables
from judogg.ingestion.application.ports import DatasetWriter
from judogg.ingestion.domain.model import Competition, Inclusion, ParsedContest, QualityIssue, Ruleset
from judogg.text import fold

# All FK-linked app tables are listed, so no CASCADE is needed; weight_category is never truncated.
TRUNCATE_APP_TABLES = (
    "TRUNCATE app.score, app.penalty, app.data_quality_issue, app.contest, app.athlete, app.tag, "
    "app.competition, app.ruleset RESTART IDENTITY"
)


class PostgresDatasetRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @contextmanager
    def rebuild(self) -> Iterator[DatasetWriter]:
        """While the transaction runs, TRUNCATE blocks readers: they wait and never see partial data."""
        with self._engine.begin() as conn:
            conn.execute(text(TRUNCATE_APP_TABLES))
            yield _Writer(conn)

    def table_counts(self) -> dict[str, int]:
        with self._engine.connect() as conn:
            return {
                table.name: int(conn.execute(select(func.count()).select_from(table)).scalar_one())
                for table in tables.APP_TABLES
            }


class _Writer:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def add_rulesets(self, rulesets: Sequence[Ruleset]) -> None:
        self._insert(
            tables.ruleset,
            [
                {
                    "id": r.id,
                    "has_koka": r.key.has_koka,
                    "has_yuko": r.key.has_yuko,
                    "max_wazaari": r.key.max_wazaari,
                    "max_shido": r.key.max_shido,
                    "year_from": r.year_from,
                    "year_to": r.year_to,
                    "label": r.label,
                }
                for r in rulesets
            ],
        )

    def add_competitions(self, competitions: Sequence[Competition]) -> None:
        self._insert(tables.competition, [asdict(c) for c in competitions])

    def set_inclusion(self, competition_id: int, inclusion: Inclusion) -> None:
        self._conn.execute(
            update(tables.competition)
            .where(tables.competition.c.id == competition_id)
            .values(exclusion_reason=inclusion.exclusion_reason, tag_coverage=inclusion.tag_coverage)
        )

    def add_contests(self, contests: Sequence[ParsedContest]) -> None:
        """Contests in chronological order: the last occurrence of an athlete gives their names and country."""
        athletes = {a.id: a for c in contests for a in c.athletes}
        if athletes:
            statement = insert(tables.athlete).values(
                [
                    {
                        "id": a.id,
                        "family_name": a.family_name,
                        "given_name": a.given_name,
                        "country_code": a.country_code,
                        "search_name": fold(f"{a.given_name} {a.family_name}"),
                        "search_name_rev": fold(f"{a.family_name} {a.given_name}"),
                    }
                    for a in athletes.values()
                ]
            )
            self._conn.execute(
                statement.on_conflict_do_update(
                    index_elements=[tables.athlete.c.id],
                    set_={
                        name: statement.excluded[name]
                        for name in ("family_name", "given_name", "country_code", "search_name", "search_name_rev")
                    },
                )
            )
        tags = {t.id: t for c in contests for t in c.tags}
        if tags:
            # A new id_tag reusing an existing code violates tag.code UNIQUE and fails the load on purpose.
            self._conn.execute(
                insert(tables.tag)
                .values([asdict(t) for t in tags.values()])
                .on_conflict_do_nothing(index_elements=[tables.tag.c.id])
            )
        self._insert(tables.contest, [_flatten(asdict(c.contest)) for c in contests])
        self._insert(tables.score, [_flatten(asdict(s)) for c in contests for s in c.scores])
        self._insert(tables.penalty, [_flatten(asdict(p)) for c in contests for p in c.penalties])
        self.add_issues([issue for c in contests for issue in c.issues])

    def add_issues(self, issues: Sequence[QualityIssue]) -> None:
        self._insert(
            tables.data_quality_issue,
            [
                {"contest_id": i.contest_id, "event_id": i.event_id, "code": i.code, "detail": dict(i.detail)}
                for i in issues
            ],
        )

    def _insert(self, table: Table, rows: list[dict[str, Any]]) -> None:
        if rows:
            self._conn.execute(insert(table), rows)


def _flatten(row: dict[str, Any]) -> dict[str, Any]:
    dims: dict[str, Any] = row.pop("dims")
    return {**row, **dims}
