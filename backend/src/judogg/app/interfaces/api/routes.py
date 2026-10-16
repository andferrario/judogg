from typing import Annotated

from fastapi import APIRouter, Depends, Query

from judogg.app.application.use_cases import (
    GetAthlete,
    GetCounters,
    GetMeta,
    GetOutcomes,
    GetOverview,
    GetPenalties,
    GetRepertoire,
    GetRepertoirePairs,
    GetTechniqueDetail,
    GetTechniqueScores,
    GetTierList,
    GetWeightMatrix,
    SearchAthletes,
)
from judogg.app.domain.athletes import AthleteResponse, AthleteSearch
from judogg.app.domain.counters import Counters
from judogg.app.domain.meta import Meta
from judogg.app.domain.outcomes import OutcomeTable
from judogg.app.domain.overview import Overview
from judogg.app.domain.penalties import Penalties
from judogg.app.domain.repertoire import Repertoire, RepertoirePairs
from judogg.app.domain.score_list import TechniqueScores
from judogg.app.domain.technique_detail import TechniqueDetail
from judogg.app.domain.techniques import TierList
from judogg.app.domain.weight_matrix import WeightMatrix
from judogg.app.interfaces.api.dependencies import ServicesDep
from judogg.app.interfaces.api.schemas import ERROR_RESPONSES, Envelope, enveloped, filter_params, present

router = APIRouter(prefix="/api")


@router.get("/meta")
def meta(services: ServicesDep) -> Meta:
    return GetMeta(services.reader, services.thresholds, services.glossary).execute()


FilterParams = Annotated[dict[str, str], Depends(filter_params)]


@router.get("/overview", responses=ERROR_RESPONSES)
def overview(params: FilterParams, services: ServicesDep) -> Envelope[Overview]:
    return enveloped(Envelope[Overview], GetOverview(services.reader, services.thresholds).execute(params))


@router.get("/techniques", responses=ERROR_RESPONSES)
def techniques(
    params: FilterParams,
    services: ServicesDep,
    sort: str | None = None,
    order: str | None = None,
    limit: str | None = None,
) -> Envelope[TierList]:
    query = params | present(sort=sort, order=order, limit=limit)
    return enveloped(Envelope[TierList], GetTierList(services.reader, services.thresholds).execute(query))


@router.get("/techniques/by-weight", responses=ERROR_RESPONSES)
def techniques_by_weight(params: FilterParams, services: ServicesDep, top: str | None = None) -> Envelope[WeightMatrix]:
    query = params | present(top=top)
    return enveloped(Envelope[WeightMatrix], GetWeightMatrix(services.reader, services.thresholds).execute(query))


@router.get("/techniques/{code}", responses=ERROR_RESPONSES)
def technique_detail(code: str, params: FilterParams, services: ServicesDep) -> Envelope[TechniqueDetail]:
    result = GetTechniqueDetail(services.reader, services.thresholds).execute(code, params)
    return enveloped(Envelope[TechniqueDetail], result)


@router.get("/techniques/{code}/scores", responses=ERROR_RESPONSES)
def technique_scores(
    code: str,
    params: FilterParams,
    services: ServicesDep,
    score_value: str | None = None,
    page: str | None = None,
    page_size: str | None = None,
) -> Envelope[TechniqueScores]:
    query = params | present(score_value=score_value, page=page, page_size=page_size)
    return enveloped(
        Envelope[TechniqueScores], GetTechniqueScores(services.reader, services.thresholds).execute(code, query)
    )


@router.get("/penalties", responses=ERROR_RESPONSES)
def penalties(params: FilterParams, services: ServicesDep) -> Envelope[Penalties]:
    return enveloped(Envelope[Penalties], GetPenalties(services.reader, services.thresholds).execute(params))


@router.get("/outcomes", responses=ERROR_RESPONSES)
def outcome_table(params: FilterParams, services: ServicesDep) -> Envelope[OutcomeTable]:
    return enveloped(Envelope[OutcomeTable], GetOutcomes(services.reader, services.thresholds).execute(params))


@router.get("/repertoire", responses=ERROR_RESPONSES)
def repertoire(
    params: FilterParams,
    services: ServicesDep,
    technique: str | None = None,
    with_: Annotated[str | None, Query(alias="with")] = None,
) -> Envelope[Repertoire]:
    query = params | present(technique=technique) | present(**{"with": with_})
    return enveloped(Envelope[Repertoire], GetRepertoire(services.reader, services.thresholds).execute(query))


@router.get("/repertoire/pairs", responses=ERROR_RESPONSES)
def repertoire_pairs(params: FilterParams, services: ServicesDep, top: str | None = None) -> Envelope[RepertoirePairs]:
    query = params | present(top=top)
    return enveloped(Envelope[RepertoirePairs], GetRepertoirePairs(services.reader, services.thresholds).execute(query))


@router.get("/counters", responses=ERROR_RESPONSES)
def counters(params: FilterParams, services: ServicesDep, technique: str | None = None) -> Envelope[Counters]:
    query = params | present(technique=technique)
    return enveloped(Envelope[Counters], GetCounters(services.reader, services.thresholds).execute(query))


@router.get("/athletes", responses=ERROR_RESPONSES)
def athletes(services: ServicesDep, q: str | None = None, limit: str | None = None) -> AthleteSearch:
    return SearchAthletes(services.reader).execute(present(q=q, limit=limit))


@router.get("/athletes/{athlete_id}", responses=ERROR_RESPONSES)
def athlete(
    athlete_id: str,
    services: ServicesDep,
    similar_scope: str | None = None,
    min_scores_athlete: str | None = None,
) -> AthleteResponse:
    params = present(similar_scope=similar_scope, min_scores_athlete=min_scores_athlete)
    return GetAthlete(services.reader, services.thresholds).execute(athlete_id, params)
