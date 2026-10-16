from dataclasses import dataclass

from judogg.app.application import lookups
from judogg.app.application.errors import InvalidParameter, NotFound
from judogg.app.application.filters import resolve_filters
from judogg.app.application.params import Params, choice, int_param, integer, members, text
from judogg.app.application.ports import DatasetReader
from judogg.app.application.results import Filtered
from judogg.app.domain.athletes import SIMILAR_SCOPES, AthleteResponse, AthleteSearch, build_athlete, build_search
from judogg.app.domain.counters import Counters, build_counters
from judogg.app.domain.envelope import totals, warnings
from judogg.app.domain.meta import GlossaryEntry, Meta, build_meta
from judogg.app.domain.model import (
    DEFAULT_MIN_SCORES_ATHLETE,
    SCORE_VALUES,
    Catalogue,
    ContestRow,
    Filters,
    PenaltyRow,
    ScoreRow,
    Thresholds,
)
from judogg.app.domain.outcomes import OutcomeTable, build_outcome_table
from judogg.app.domain.overview import Overview, build_overview
from judogg.app.domain.penalties import Penalties, build_penalties
from judogg.app.domain.refs import technique_ref
from judogg.app.domain.repertoire import Repertoire, RepertoirePairs, build_pairs, build_repertoire
from judogg.app.domain.score_list import TechniqueScores, newest_first, score_list_row
from judogg.app.domain.technique_detail import TechniqueDetail, build_technique_detail
from judogg.app.domain.techniques import SORT_KEYS, SORT_ORDERS, TierList, build_tier_list
from judogg.app.domain.weight_matrix import WeightMatrix, build_weight_matrix
from judogg.text import fold


@dataclass(frozen=True)
class FilteredRows:
    scores: list[ScoreRow]
    contests: list[ContestRow]
    penalties: list[PenaltyRow]


def load_rows(reader: DatasetReader, filters: Filters) -> FilteredRows:
    return FilteredRows(reader.scores(filters), reader.contests(filters), reader.penalties(filters))


def wrap[T](
    filters: Filters,
    catalogue: Catalogue,
    thresholds: Thresholds,
    rows: FilteredRows,
    data: T,
    *,
    scores_analysed: bool = True,
) -> Filtered[T]:
    analysed = rows.scores if scores_analysed else None
    return Filtered(
        filters=filters,
        totals=totals(rows.scores, rows.contests, rows.penalties),
        warnings=warnings(filters, catalogue.rulesets, analysed, rows.contests, thresholds),
        data=data,
    )


class GetMeta:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds, glossary: tuple[GlossaryEntry, ...]) -> None:
        self._reader = reader
        self._thresholds = thresholds
        self._glossary = glossary

    def execute(self) -> Meta:
        return build_meta(
            self._reader.catalogue(),
            self._reader.contests(None),
            self._reader.scores(None),
            self._reader.table_counts(),
            self._reader.quality_issues(),
            self._thresholds,
            self._glossary,
        )


class GetOverview:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds) -> None:
        self._reader = reader
        self._thresholds = thresholds

    def execute(self, params: Params) -> Filtered[Overview]:
        catalogue = self._reader.catalogue()
        filters = resolve_filters(params, catalogue)
        rows = load_rows(self._reader, filters)
        overview = build_overview(rows.scores, rows.contests, self._thresholds)
        return wrap(filters, catalogue, self._thresholds, rows, overview)


class GetTierList:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds) -> None:
        self._reader = reader
        self._thresholds = thresholds

    def execute(self, params: Params) -> Filtered[TierList]:
        catalogue = self._reader.catalogue()
        filters = resolve_filters(params, catalogue)
        sort = choice(params, "sort", SORT_KEYS, "share")
        order = choice(params, "order", SORT_ORDERS, "desc")
        limit = int_param(params, "limit", 50, 1, 200)
        rows = load_rows(self._reader, filters)
        tier_list = build_tier_list(rows.scores, catalogue.tags, filters.count_by, sort, order, limit, self._thresholds)
        return wrap(filters, catalogue, self._thresholds, rows, tier_list)


class GetTechniqueDetail:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds) -> None:
        self._reader = reader
        self._thresholds = thresholds

    def execute(self, code: str, params: Params) -> Filtered[TechniqueDetail]:
        catalogue = self._reader.catalogue()
        tag = lookups.technique(catalogue, code, "technique")
        filters = resolve_filters(params, catalogue)
        rows = load_rows(self._reader, filters)
        athletes = self._reader.athletes({s.athlete_id for s in rows.scores if s.technique_tag_id == tag.id})
        detail = build_technique_detail(tag, rows.scores, filters, catalogue, athletes, self._thresholds)
        return wrap(filters, catalogue, self._thresholds, rows, detail)


class GetTechniqueScores:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds) -> None:
        self._reader = reader
        self._thresholds = thresholds

    def execute(self, code: str, params: Params) -> Filtered[TechniqueScores]:
        catalogue = self._reader.catalogue()
        tag = lookups.technique(catalogue, code, "technique")
        filters = resolve_filters(params, catalogue)
        values = members(params, "score_value", SCORE_VALUES)
        page = int_param(params, "page", 1, 1, 100_000)
        page_size = int_param(params, "page_size", 20, 1, 100)
        rows = load_rows(self._reader, filters)
        matching = [s for s in rows.scores if s.technique_tag_id == tag.id and s.score_value in values]
        shown = newest_first(matching, catalogue.competitions)[(page - 1) * page_size : page * page_size]
        athletes = self._reader.athletes({a for s in shown for a in (s.athlete_id, s.opponent_id)})
        contests = {c.id: c for c in rows.contests}
        result = TechniqueScores(
            technique=technique_ref(tag),
            rows=tuple(score_list_row(s, catalogue, contests, athletes) for s in shown),
            page=page,
            page_size=page_size,
            total=len(matching),
        )
        return wrap(filters, catalogue, self._thresholds, rows, result)


class GetWeightMatrix:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds) -> None:
        self._reader = reader
        self._thresholds = thresholds

    def execute(self, params: Params) -> Filtered[WeightMatrix]:
        catalogue = self._reader.catalogue()
        filters = resolve_filters(params, catalogue)
        top = int_param(params, "top", 8, 1, 20)
        rows = load_rows(self._reader, filters)
        matrix = build_weight_matrix(rows.scores, filters, catalogue, top, self._thresholds)
        return wrap(filters, catalogue, self._thresholds, rows, matrix)


class GetPenalties:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds) -> None:
        self._reader = reader
        self._thresholds = thresholds

    def execute(self, params: Params) -> Filtered[Penalties]:
        catalogue = self._reader.catalogue()
        filters = resolve_filters(params, catalogue)
        rows = load_rows(self._reader, filters)
        result = build_penalties(rows.penalties, rows.contests, filters, catalogue, self._thresholds)
        return wrap(filters, catalogue, self._thresholds, rows, result, scores_analysed=False)


class GetOutcomes:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds) -> None:
        self._reader = reader
        self._thresholds = thresholds

    def execute(self, params: Params) -> Filtered[OutcomeTable]:
        catalogue = self._reader.catalogue()
        filters = resolve_filters(params, catalogue)
        rows = load_rows(self._reader, filters)
        table = build_outcome_table(rows.contests, rows.penalties, filters, catalogue, self._thresholds)
        return wrap(filters, catalogue, self._thresholds, rows, table, scores_analysed=False)


class GetRepertoire:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds) -> None:
        self._reader = reader
        self._thresholds = thresholds

    def execute(self, params: Params) -> Filtered[Repertoire]:
        catalogue = self._reader.catalogue()
        filters = resolve_filters(params, catalogue)
        technique = lookups.technique(catalogue, lookups.required(params, "technique"), "technique")
        companion_code = text(params, "with")
        companion = lookups.technique(catalogue, companion_code, "with") if companion_code else None
        if companion is not None and companion.id == technique.id:
            raise InvalidParameter("with", "with must be different from technique")
        rows = load_rows(self._reader, filters)
        athletes = self._reader.athletes({s.athlete_id for s in rows.scores})
        result = build_repertoire(technique, companion, rows.scores, filters, catalogue, athletes, self._thresholds)
        return wrap(filters, catalogue, self._thresholds, rows, result)


class GetRepertoirePairs:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds) -> None:
        self._reader = reader
        self._thresholds = thresholds

    def execute(self, params: Params) -> Filtered[RepertoirePairs]:
        catalogue = self._reader.catalogue()
        filters = resolve_filters(params, catalogue)
        top = int_param(params, "top", 10, 2, 20)
        rows = load_rows(self._reader, filters)
        result = build_pairs(rows.scores, filters, catalogue, top, self._thresholds)
        return wrap(filters, catalogue, self._thresholds, rows, result)


class GetCounters:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds) -> None:
        self._reader = reader
        self._thresholds = thresholds

    def execute(self, params: Params) -> Filtered[Counters]:
        catalogue = self._reader.catalogue()
        filters = resolve_filters(params, catalogue)
        technique = lookups.technique(catalogue, lookups.required(params, "technique"), "technique")
        rows = load_rows(self._reader, filters)
        athletes = self._reader.athletes({s.athlete_id for s in rows.scores})
        result = build_counters(technique, rows.scores, filters, catalogue, athletes, self._thresholds)
        return wrap(filters, catalogue, self._thresholds, rows, result)


class SearchAthletes:
    def __init__(self, reader: DatasetReader) -> None:
        self._reader = reader

    def execute(self, params: Params) -> AthleteSearch:
        term = fold((params.get("q") or "").strip())
        if len(term) < 2:
            raise InvalidParameter("q", "q must have at least 2 characters")
        limit = int_param(params, "limit", 10, 1, 50)
        matches = self._reader.search_athletes(term)
        ids = [a.id for a in matches]
        contests = self._reader.contests_of_athletes(ids)
        scores = self._reader.scores_of_athletes(ids)
        return build_search(matches, contests, scores, self._reader.catalogue(), limit)


class GetAthlete:
    def __init__(self, reader: DatasetReader, thresholds: Thresholds) -> None:
        self._reader = reader
        self._thresholds = thresholds

    def execute(self, athlete_id: str, params: Params) -> AthleteResponse:
        number = integer(athlete_id)
        athletes = self._reader.athletes(None)
        if number is None or number not in athletes:
            raise NotFound("athlete", f"unknown athlete {athlete_id}")
        scope = choice(params, "similar_scope", SIMILAR_SCOPES, "weight")
        min_scores = int_param(params, "min_scores_athlete", DEFAULT_MIN_SCORES_ATHLETE, 1, 50)
        return build_athlete(
            athletes[number],
            scope,
            min_scores,
            self._reader.contests(None),
            self._reader.scores(None),
            self._reader.catalogue(),
            athletes,
            self._thresholds,
        )
