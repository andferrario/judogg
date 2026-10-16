from collections.abc import Iterator, Mapping
from typing import Any

from sqlalchemy import Engine, func, select
from sqlalchemy.dialects.postgresql import insert

from judogg.db.tables import raw_response
from judogg.ingestion.application.raw_responses import CONTESTS, RawResponse, params_hash


class PostgresRawResponseRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save(self, response: RawResponse) -> None:
        values = {
            "endpoint": response.endpoint,
            "params_hash": params_hash(response.params),
            "params": dict(response.params),
            "competition_id": response.competition_id,
            "payload": response.payload,
        }
        statement = insert(raw_response).values(values)
        statement = statement.on_conflict_do_update(
            index_elements=[raw_response.c.endpoint, raw_response.c.params_hash],
            set_={
                "params": statement.excluded.params,
                "competition_id": statement.excluded.competition_id,
                "payload": statement.excluded.payload,
                "fetched_at": func.now(),
            },
        )
        with self._engine.begin() as conn:
            conn.execute(statement)

    def get(self, endpoint: str, params: Mapping[str, str]) -> Any | None:
        query = select(raw_response.c.payload).where(
            raw_response.c.endpoint == endpoint, raw_response.c.params_hash == params_hash(params)
        )
        with self._engine.connect() as conn:
            return conn.execute(query).scalar_one_or_none()

    def contest_competition_ids(self) -> list[int]:
        query = (
            select(raw_response.c.competition_id)
            .where(raw_response.c.endpoint == CONTESTS)
            .distinct()
            .order_by(raw_response.c.competition_id)
        )
        with self._engine.connect() as conn:
            return [int(value) for value in conn.execute(query).scalars()]

    def contest_payloads(self, competition_id: int) -> Iterator[Any]:
        """One competition at a time (a few MB): the whole history (1–2 GB) never fits in memory."""
        query = (
            select(raw_response.c.payload)
            .where(raw_response.c.endpoint == CONTESTS, raw_response.c.competition_id == competition_id)
            .order_by(raw_response.c.params_hash)
        )
        with self._engine.connect() as conn:
            payloads = list(conn.execute(query).scalars())
        yield from payloads
