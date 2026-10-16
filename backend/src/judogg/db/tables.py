"""Columns, keys and nullability only: CHECK constraints and indexes live in the migrations."""

from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Identity,
    Integer,
    MetaData,
    Numeric,
    SmallInteger,
    Table,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP

__all__ = ["APP_TABLES", "Table", "metadata"]

metadata = MetaData()


def _dimensions() -> list[Column[Any]]:
    """Copied onto every fact table, so that filtered aggregations need no join."""
    return [
        Column("competition_id", Integer, ForeignKey("app.competition.id"), nullable=False),
        Column("year", SmallInteger, nullable=False),
        Column("ruleset_id", SmallInteger, ForeignKey("app.ruleset.id"), nullable=False),
        Column("gender", Text, nullable=False),
        Column("weight_category_id", SmallInteger, ForeignKey("app.weight_category.id"), nullable=False),
    ]


raw_response = Table(
    "raw_response",
    metadata,
    Column("endpoint", Text, primary_key=True),
    Column("params_hash", Text, primary_key=True),
    Column("params", JSONB, nullable=False),
    Column("competition_id", Integer),
    Column("payload", JSONB, nullable=False),
    Column("fetched_at", TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
    schema="ingestion",
)

ruleset = Table(
    "ruleset",
    metadata,
    Column("id", SmallInteger, primary_key=True, autoincrement=False),
    Column("has_koka", Boolean, nullable=False),
    Column("has_yuko", Boolean, nullable=False),
    Column("max_wazaari", SmallInteger),
    Column("max_shido", SmallInteger, nullable=False),
    Column("year_from", SmallInteger, nullable=False),
    Column("year_to", SmallInteger, nullable=False),
    Column("label", Text, nullable=False),
    schema="app",
)

weight_category = Table(
    "weight_category",
    metadata,
    Column("id", SmallInteger, primary_key=True, autoincrement=False),
    Column("code", Text, nullable=False, unique=True),
    Column("gender", Text, nullable=False),
    Column("label", Text, nullable=False),
    Column("sort_order", SmallInteger, nullable=False, unique=True),
    schema="app",
)

competition = Table(
    "competition",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("code", Text),
    Column("name", Text, nullable=False),
    Column("rank_name", Text, nullable=False),
    Column("date_from", Date, nullable=False),
    Column("date_to", Date, nullable=False),
    Column("year", SmallInteger, nullable=False),
    Column("ruleset_id", SmallInteger, ForeignKey("app.ruleset.id"), nullable=False),
    Column("level", Text, nullable=False),
    Column("tag_coverage", Numeric(5, 4)),
    Column("exclusion_reason", Text),
    schema="app",
)

athlete = Table(
    "athlete",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("family_name", Text, nullable=False),
    Column("given_name", Text, nullable=False),
    Column("country_code", Text, nullable=False),
    Column("search_name", Text, nullable=False),
    Column("search_name_rev", Text, nullable=False),
    schema="app",
)

tag = Table(
    "tag",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("code", Text, nullable=False, unique=True),
    Column("name", Text, nullable=False),
    Column("kind", Text, nullable=False),
    Column("group_label", Text),
    Column("domain", Text),
    schema="app",
)

contest = Table(
    "contest",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=False),
    Column("code", Text, nullable=False),
    *_dimensions(),
    Column("white_athlete_id", Integer, ForeignKey("app.athlete.id"), nullable=False),
    Column("blue_athlete_id", Integer, ForeignKey("app.athlete.id"), nullable=False),
    Column("white_country_code", Text, nullable=False),
    Column("blue_country_code", Text, nullable=False),
    Column("end_type", Text, nullable=False),
    Column("went_gs", Boolean, nullable=False),
    Column("duration_s", Integer, nullable=False),
    Column("has_quality_issue", Boolean, nullable=False),
    schema="app",
)

score = Table(
    "score",
    metadata,
    Column("id", BigInteger, Identity(always=True), primary_key=True),
    Column("event_id", BigInteger, nullable=False),
    Column("contest_id", BigInteger, ForeignKey("app.contest.id"), nullable=False),
    *_dimensions(),
    Column("athlete_id", Integer, ForeignKey("app.athlete.id"), nullable=False),
    Column("athlete_country", Text, nullable=False),
    Column("opponent_id", Integer, ForeignKey("app.athlete.id"), nullable=False),
    Column("score_value", Text, nullable=False),
    Column("is_awasete", Boolean, nullable=False),
    Column("technique_tag_id", Integer, ForeignKey("app.tag.id")),
    Column("technique_domain", Text, nullable=False),
    Column("direction", Text, nullable=False),
    Column("is_gs", Boolean, nullable=False),
    Column("time_bin", SmallInteger, nullable=False),
    schema="app",
)

penalty = Table(
    "penalty",
    metadata,
    Column("id", BigInteger, Identity(always=True), primary_key=True),
    Column("event_id", BigInteger, nullable=False),
    Column("contest_id", BigInteger, ForeignKey("app.contest.id"), nullable=False),
    *_dimensions(),
    Column("athlete_id", Integer, ForeignKey("app.athlete.id"), nullable=False),
    Column("athlete_country", Text, nullable=False),
    Column("penalty_kind", Text, nullable=False),
    Column("shido_number", SmallInteger, nullable=False),
    Column("reason_tag_id", Integer, ForeignKey("app.tag.id")),
    Column("is_gs", Boolean, nullable=False),
    Column("time_bin", SmallInteger, nullable=False),
    schema="app",
)

data_quality_issue = Table(
    "data_quality_issue",
    metadata,
    Column("id", BigInteger, Identity(always=True), primary_key=True),
    Column("contest_id", BigInteger),
    Column("event_id", BigInteger),
    Column("code", Text, nullable=False),
    Column("detail", JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    schema="app",
)

# Every table rewritten by a load, in an order that respects the foreign keys (parents first).
APP_TABLES: tuple[Table, ...] = (ruleset, competition, athlete, tag, contest, score, penalty, data_quality_issue)
