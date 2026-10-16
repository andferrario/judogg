from collections.abc import Collection
from typing import Any

from sqlalchemy import ColumnElement, Connection, Engine, Row, Table, func, or_, select

from judogg.app.domain.model import (
    Athlete,
    Catalogue,
    Competition,
    ContestRow,
    Filters,
    IssueRow,
    PenaltyRow,
    Ruleset,
    ScoreRow,
    TableCounts,
    Tag,
    WeightCategory,
)
from judogg.db import tables


class PostgresDatasetReader:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def catalogue(self) -> Catalogue:
        contest = tables.contest
        with self._engine.connect() as conn:
            contests_per_ruleset = {
                row.ruleset_id: row.n
                for row in conn.execute(
                    select(contest.c.ruleset_id, func.count().label("n")).group_by(contest.c.ruleset_id)
                )
            }
            weights = tuple(
                WeightCategory(r.code, r.gender, r.label, r.sort_order)
                for r in conn.execute(select(tables.weight_category).order_by(tables.weight_category.c.sort_order))
            )
            rulesets = tuple(
                Ruleset(
                    r.id,
                    r.label,
                    r.year_from,
                    r.year_to,
                    r.has_koka,
                    r.has_yuko,
                    r.max_wazaari,
                    r.max_shido,
                    contests_per_ruleset.get(r.id, 0),
                )
                for r in conn.execute(select(tables.ruleset).order_by(tables.ruleset.c.id))
            )
            tags = {
                r.id: Tag(r.id, r.code, r.name, r.kind, r.group_label, r.domain)
                for r in conn.execute(select(tables.tag))
            }
            competitions = {
                r.id: Competition(
                    r.id,
                    r.code,
                    r.name,
                    r.rank_name,
                    r.level,
                    r.date_from,
                    r.date_to,
                    r.year,
                    r.ruleset_id,
                    None if r.tag_coverage is None else float(r.tag_coverage),
                    r.exclusion_reason,
                )
                for r in conn.execute(select(tables.competition))
            }
        return Catalogue(weights, rulesets, tags, competitions)

    def scores(self, filters: Filters | None) -> list[ScoreRow]:
        score = tables.score
        query = select(score).order_by(score.c.id)
        with self._engine.connect() as conn:
            codes, ids = _weight_codes(conn)
            if filters is not None:
                query = query.where(
                    *_dimensions(score, filters, ids),
                    score.c.direction.in_(filters.side),
                    score.c.technique_domain.in_(filters.domain),
                )
                if filters.country:
                    query = query.where(score.c.athlete_country.in_(filters.country))
            return [_score_row(r, codes) for r in conn.execute(query)]

    def contests(self, filters: Filters | None) -> list[ContestRow]:
        contest = tables.contest
        query = select(contest).order_by(contest.c.id)
        with self._engine.connect() as conn:
            codes, ids = _weight_codes(conn)
            if filters is not None:
                query = query.where(*_dimensions(contest, filters, ids))
                if filters.country:
                    query = query.where(
                        or_(
                            contest.c.white_country_code.in_(filters.country),
                            contest.c.blue_country_code.in_(filters.country),
                        )
                    )
            return [_contest_row(r, codes) for r in conn.execute(query)]

    def penalties(self, filters: Filters | None) -> list[PenaltyRow]:
        penalty = tables.penalty
        query = select(penalty).order_by(penalty.c.id)
        with self._engine.connect() as conn:
            codes, ids = _weight_codes(conn)
            if filters is not None:
                query = query.where(*_dimensions(penalty, filters, ids))
                if filters.country:
                    query = query.where(penalty.c.athlete_country.in_(filters.country))
            return [
                PenaltyRow(
                    r.event_id,
                    r.contest_id,
                    codes[r.weight_category_id],
                    r.athlete_id,
                    r.penalty_kind,
                    r.shido_number,
                    r.reason_tag_id,
                    r.time_bin,
                )
                for r in conn.execute(query)
            ]

    def table_counts(self) -> TableCounts:
        with self._engine.connect() as conn:
            athletes = conn.execute(select(func.count()).select_from(tables.athlete)).scalar_one()
            penalties = conn.execute(select(func.count()).select_from(tables.penalty)).scalar_one()
        return TableCounts(int(athletes), int(penalties))

    def quality_issues(self) -> list[IssueRow]:
        issue = tables.data_quality_issue
        with self._engine.connect() as conn:
            rows = conn.execute(select(issue.c.code, issue.c.contest_id).order_by(issue.c.id))
            return [IssueRow(r.code, r.contest_id) for r in rows]

    def athletes(self, ids: Collection[int] | None) -> dict[int, Athlete]:
        athlete = tables.athlete
        query = select(athlete.c.id, athlete.c.given_name, athlete.c.family_name, athlete.c.country_code)
        if ids is not None:
            query = query.where(athlete.c.id.in_(list(ids)))
        with self._engine.connect() as conn:
            return {r.id: Athlete(r.id, r.given_name, r.family_name, r.country_code) for r in conn.execute(query)}

    def search_athletes(self, term: str) -> list[Athlete]:
        athlete = tables.athlete
        pattern = _like_pattern(term)
        query = (
            select(athlete.c.id, athlete.c.given_name, athlete.c.family_name, athlete.c.country_code)
            .where(
                or_(
                    athlete.c.search_name.like(pattern, escape="\\"),
                    athlete.c.search_name_rev.like(pattern, escape="\\"),
                )
            )
            .order_by(athlete.c.id)
        )
        with self._engine.connect() as conn:
            return [Athlete(r.id, r.given_name, r.family_name, r.country_code) for r in conn.execute(query)]

    def contests_of_athletes(self, ids: Collection[int]) -> list[ContestRow]:
        contest = tables.contest
        wanted = list(ids)
        query = (
            select(contest)
            .where(or_(contest.c.white_athlete_id.in_(wanted), contest.c.blue_athlete_id.in_(wanted)))
            .order_by(contest.c.id)
        )
        with self._engine.connect() as conn:
            codes, _ = _weight_codes(conn)
            return [_contest_row(r, codes) for r in conn.execute(query)]

    def scores_of_athletes(self, ids: Collection[int]) -> list[ScoreRow]:
        score = tables.score
        query = select(score).where(score.c.athlete_id.in_(list(ids))).order_by(score.c.id)
        with self._engine.connect() as conn:
            codes, _ = _weight_codes(conn)
            return [_score_row(r, codes) for r in conn.execute(query)]


def _score_row(r: Row[Any], codes: dict[int, str]) -> ScoreRow:
    return ScoreRow(
        r.event_id,
        r.contest_id,
        r.competition_id,
        r.year,
        codes[r.weight_category_id],
        r.athlete_id,
        r.athlete_country,
        r.opponent_id,
        r.score_value,
        r.is_awasete,
        r.technique_tag_id,
        r.direction,
        r.is_gs,
        r.time_bin,
    )


def _contest_row(r: Row[Any], codes: dict[int, str]) -> ContestRow:
    return ContestRow(
        r.id,
        r.code,
        r.competition_id,
        r.year,
        r.ruleset_id,
        codes[r.weight_category_id],
        r.white_athlete_id,
        r.blue_athlete_id,
        r.white_country_code,
        r.blue_country_code,
        r.end_type,
        r.went_gs,
        r.duration_s,
        r.has_quality_issue,
    )


def _like_pattern(term: str) -> str:
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _weight_codes(conn: Connection) -> tuple[dict[int, str], dict[str, int]]:
    rows = conn.execute(select(tables.weight_category.c.id, tables.weight_category.c.code)).all()
    return {r.id: r.code for r in rows}, {r.code: r.id for r in rows}


def _dimensions(table: Table, filters: Filters, ids: dict[str, int]) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = [table.c.ruleset_id.in_(filters.ruleset)]
    if filters.year_from is not None:
        conditions.append(table.c.year >= filters.year_from)
    if filters.year_to is not None:
        conditions.append(table.c.year <= filters.year_to)
    if filters.gender != "all":
        conditions.append(table.c.gender == filters.gender)
    if filters.weight:
        conditions.append(table.c.weight_category_id.in_([ids[code] for code in filters.weight]))
    return conditions
