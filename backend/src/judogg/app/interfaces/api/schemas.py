from typing import Literal

from pydantic import BaseModel

from judogg.app.application.results import Filtered
from judogg.app.domain.envelope import Totals, WarningItem
from judogg.app.domain.model import Filters


class ErrorDetail(BaseModel):
    code: Literal["invalid_parameter", "not_found"]
    message: str
    field: str | None


class ErrorBody(BaseModel):
    error: ErrorDetail


ERROR_RESPONSES: dict[int | str, dict[str, object]] = {400: {"model": ErrorBody}, 404: {"model": ErrorBody}}


class Envelope[T](BaseModel):
    filters: Filters
    totals: Totals
    warnings: list[WarningItem]
    data: T


def enveloped[T](model: type[Envelope[T]], result: Filtered[T]) -> Envelope[T]:
    """`model` is the concrete envelope (e.g. `Envelope[Overview]`), so that `data` is validated as that shape."""
    return model(filters=result.filters, totals=result.totals, warnings=list(result.warnings), data=result.data)


def present(**values: str | None) -> dict[str, str]:
    return {name: value for name, value in values.items() if value is not None}


def filter_params(
    gender: str | None = None,
    weight: str | None = None,
    ruleset: str | None = None,
    year_from: str | None = None,
    year_to: str | None = None,
    country: str | None = None,
    side: str | None = None,
    domain: str | None = None,
    count_by: str | None = None,
    min_scores_athlete: str | None = None,
    min_scores_technique: str | None = None,
) -> dict[str, str]:
    """Strings on purpose: validation and defaults belong to the application, with the API's error format."""
    return present(
        gender=gender,
        weight=weight,
        ruleset=ruleset,
        year_from=year_from,
        year_to=year_to,
        country=country,
        side=side,
        domain=domain,
        count_by=count_by,
        min_scores_athlete=min_scores_athlete,
        min_scores_technique=min_scores_technique,
    )
