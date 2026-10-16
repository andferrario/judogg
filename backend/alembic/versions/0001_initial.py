"""Initial schemas: ingestion.raw_response and the app tables.

Revision ID: 0001
Revises:
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

STATEMENTS = [
    "CREATE SCHEMA ingestion",
    """CREATE TABLE ingestion.raw_response (
      endpoint text NOT NULL, params_hash text NOT NULL, params jsonb NOT NULL, competition_id integer,
      payload jsonb NOT NULL, fetched_at timestamptz NOT NULL DEFAULT now(),
      PRIMARY KEY (endpoint, params_hash))""",
    "CREATE INDEX ON ingestion.raw_response (competition_id)",
    "CREATE SCHEMA app",
    """CREATE TABLE app.ruleset (
      id smallint PRIMARY KEY CHECK (id = year_from), has_koka boolean NOT NULL, has_yuko boolean NOT NULL,
      max_wazaari smallint, max_shido smallint NOT NULL,
      year_from smallint NOT NULL, year_to smallint NOT NULL, label text NOT NULL,
      UNIQUE NULLS NOT DISTINCT (has_koka, has_yuko, max_wazaari, max_shido))""",
    """CREATE TABLE app.weight_category (
      id smallint PRIMARY KEY, code text NOT NULL UNIQUE,
      gender text NOT NULL CHECK (gender IN ('m','f')), label text NOT NULL, sort_order smallint NOT NULL UNIQUE)""",
    """CREATE TABLE app.competition (
      id integer PRIMARY KEY, code text, name text NOT NULL, rank_name text NOT NULL,
      date_from date NOT NULL, date_to date NOT NULL, year smallint NOT NULL,
      ruleset_id smallint NOT NULL REFERENCES app.ruleset,
      level text NOT NULL CHECK (level IN ('elite','continental')),
      tag_coverage numeric(5,4) CHECK (tag_coverage BETWEEN 0 AND 1),
      exclusion_reason text)""",
    """CREATE TABLE app.athlete (
      id integer PRIMARY KEY, family_name text NOT NULL, given_name text NOT NULL, country_code text NOT NULL,
      search_name text NOT NULL, search_name_rev text NOT NULL)""",
    """CREATE TABLE app.tag (
      id integer PRIMARY KEY, code text NOT NULL UNIQUE, name text NOT NULL,
      kind text NOT NULL CHECK (kind IN ('technique','shido_reason')), group_label text,
      domain text CHECK (domain IN ('standing','ground')), CHECK (kind = 'technique' OR domain IS NULL))""",
    """CREATE TABLE app.contest (
      id bigint PRIMARY KEY, code text NOT NULL,
      competition_id integer NOT NULL REFERENCES app.competition, year smallint NOT NULL,
      ruleset_id smallint NOT NULL REFERENCES app.ruleset, gender text NOT NULL CHECK (gender IN ('m','f')),
      weight_category_id smallint NOT NULL REFERENCES app.weight_category,
      white_athlete_id integer NOT NULL REFERENCES app.athlete, blue_athlete_id integer NOT NULL REFERENCES app.athlete,
      white_country_code text NOT NULL, blue_country_code text NOT NULL,
      end_type text NOT NULL CHECK (end_type IN ('fusen_gachi','kiken_gachi','double_hansoku','ippon',
                                                 'waza_ari_awasete','hansoku_shido','score_gs','score_regulation')),
      went_gs boolean NOT NULL, duration_s integer NOT NULL CHECK (duration_s >= 0),
      has_quality_issue boolean NOT NULL)""",
    """CREATE TABLE app.score (
      id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, event_id bigint NOT NULL,
      contest_id bigint NOT NULL REFERENCES app.contest,
      competition_id integer NOT NULL REFERENCES app.competition, year smallint NOT NULL,
      ruleset_id smallint NOT NULL REFERENCES app.ruleset, gender text NOT NULL CHECK (gender IN ('m','f')),
      weight_category_id smallint NOT NULL REFERENCES app.weight_category,
      athlete_id integer NOT NULL REFERENCES app.athlete, athlete_country text NOT NULL,
      opponent_id integer NOT NULL REFERENCES app.athlete,
      score_value text NOT NULL CHECK (score_value IN ('ippon','waza_ari','yuko')), is_awasete boolean NOT NULL,
      technique_tag_id integer REFERENCES app.tag,
      technique_domain text NOT NULL CHECK (technique_domain IN ('standing','ground','unknown')),
      direction text NOT NULL CHECK (direction IN ('left','right','unknown')),
      is_gs boolean NOT NULL, time_bin smallint NOT NULL CHECK (time_bin BETWEEN 0 AND 8),
      UNIQUE NULLS NOT DISTINCT (event_id, athlete_id, technique_tag_id))""",
    """CREATE TABLE app.penalty (
      id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, event_id bigint NOT NULL,
      contest_id bigint NOT NULL REFERENCES app.contest,
      competition_id integer NOT NULL REFERENCES app.competition, year smallint NOT NULL,
      ruleset_id smallint NOT NULL REFERENCES app.ruleset, gender text NOT NULL CHECK (gender IN ('m','f')),
      weight_category_id smallint NOT NULL REFERENCES app.weight_category,
      athlete_id integer NOT NULL REFERENCES app.athlete, athlete_country text NOT NULL,
      penalty_kind text NOT NULL CHECK (penalty_kind IN ('shido','hansoku_shido')),
      shido_number smallint NOT NULL CHECK (shido_number >= 1), reason_tag_id integer REFERENCES app.tag,
      is_gs boolean NOT NULL, time_bin smallint NOT NULL CHECK (time_bin BETWEEN 0 AND 8),
      UNIQUE (event_id, athlete_id))""",
    """CREATE TABLE app.data_quality_issue (
      id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
      contest_id bigint,  -- no FK: unknown_weight and no_events issues point at contests that are not stored
      event_id bigint,
      code text NOT NULL CHECK (code IN ('summary_mismatch','unknown_event_type','unknown_actor',
                                         'new_tag_group','unknown_weight','no_events')),
      detail jsonb NOT NULL DEFAULT '{}')""",
    "CREATE INDEX ON app.score (ruleset_id, gender, weight_category_id, year)",
    "CREATE INDEX ON app.score (technique_tag_id, ruleset_id, gender, weight_category_id)",
    "CREATE INDEX ON app.score (athlete_id)",
    "CREATE INDEX ON app.score (opponent_id)",
    "CREATE INDEX ON app.penalty (ruleset_id, gender, weight_category_id, year)",
    "CREATE INDEX ON app.penalty (reason_tag_id)",
    "CREATE INDEX ON app.contest (ruleset_id, gender, weight_category_id, year)",
    "CREATE INDEX ON app.contest (white_athlete_id)",
    "CREATE INDEX ON app.contest (blue_athlete_id)",
    """INSERT INTO app.weight_category (id, code, gender, label, sort_order) VALUES
      (1,'m-60','m','-60',1), (2,'m-66','m','-66',2), (3,'m-73','m','-73',3), (4,'m-81','m','-81',4),
      (5,'m-90','m','-90',5), (6,'m-100','m','-100',6), (7,'m+100','m','+100',7),
      (8,'f-48','f','-48',8), (9,'f-52','f','-52',9), (10,'f-57','f','-57',10), (11,'f-63','f','-63',11),
      (12,'f-70','f','-70',12), (13,'f-78','f','-78',13), (14,'f+78','f','+78',14)""",
]


def upgrade() -> None:
    for statement in STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    op.execute("DROP SCHEMA app CASCADE")
    op.execute("DROP SCHEMA ingestion CASCADE")
