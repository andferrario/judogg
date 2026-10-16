import pytest
from sqlalchemy import Engine, inspect, text
from sqlalchemy.exc import IntegrityError

from judogg.db import tables
from judogg.ingestion.domain.constants import WEIGHT_CATEGORY_IDS


@pytest.mark.parametrize("table", tables.metadata.sorted_tables, ids=lambda t: t.fullname)
def test_database_matches_the_table_definitions(engine: Engine, table: tables.Table) -> None:
    columns = {c["name"]: c["nullable"] for c in inspect(engine).get_columns(table.name, schema=table.schema)}
    assert columns == {c.name: c.nullable for c in table.columns}


def test_weight_categories_are_seeded(engine: Engine) -> None:
    with engine.connect() as conn:
        query = text("SELECT id, code, gender, label, sort_order FROM app.weight_category ORDER BY id")
        rows = conn.execute(query).all()
    assert len(rows) == 14
    assert rows[0] == (1, "m-60", "m", "-60", 1)
    assert rows[6] == (7, "m+100", "m", "+100", 7)
    assert rows[13] == (14, "f+78", "f", "+78", 14)


@pytest.mark.parametrize(
    "statement",
    [
        "INSERT INTO app.ruleset VALUES (2017, false, false, NULL, 2, 2018, 2018, 'x')",  # id must equal year_from
        "INSERT INTO app.tag VALUES (1, 'x', 'X', 'throw', NULL, NULL)",  # unknown kind
        "INSERT INTO app.tag VALUES (1, 'x', 'X', 'shido_reason', NULL, 'standing')",  # domain only on techniques
        "INSERT INTO app.data_quality_issue (code) VALUES ('other')",  # unknown issue code
    ],
)
def test_check_constraints_reject_invalid_rows(engine: Engine, statement: str) -> None:
    with engine.connect() as conn, pytest.raises(IntegrityError):
        conn.execute(text(statement))


def test_domain_weight_categories_match_the_seed(engine: Engine) -> None:
    with engine.connect() as conn:
        seeded = {str(code): int(id_) for code, id_ in conn.execute(text("SELECT code, id FROM app.weight_category"))}
    assert seeded == WEIGHT_CATEGORY_IDS
