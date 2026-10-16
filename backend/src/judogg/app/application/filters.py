import re

from judogg.app.application.errors import InvalidParameter
from judogg.app.application.params import (
    Params,
    choice,
    int_param,
    integer,
    items,
    members,
    optional_int_param,
)
from judogg.app.domain.model import (
    COUNT_BYS,
    DEFAULT_MIN_SCORES_ATHLETE,
    DEFAULT_MIN_SCORES_TECHNIQUE,
    DOMAINS,
    GENDER_FILTERS,
    SIDES,
    Catalogue,
    Filters,
)
from judogg.app.domain.rulesets import default_ruleset

_COUNTRY = re.compile(r"[A-Z]{3}")


def resolve_filters(params: Params, catalogue: Catalogue) -> Filters:
    gender = choice(params, "gender", GENDER_FILTERS, "all")
    weight = tuple(items(params, "weight"))
    categories = {w.code: w for w in catalogue.weights}
    for code in weight:
        if code not in categories:
            raise InvalidParameter("weight", f"unknown weight category {code}")
        if gender != "all" and categories[code].gender != gender:
            raise InvalidParameter("weight", f"weight category {code} does not match gender {gender}")
    rulesets = {r.id: r for r in catalogue.rulesets}
    selected = []
    for value in items(params, "ruleset"):
        ruleset_id = integer(value)
        if ruleset_id is None or ruleset_id not in rulesets:
            raise InvalidParameter("ruleset", f"unknown ruleset {value}")
        selected.append(rulesets[ruleset_id])
    if not selected:
        default = default_ruleset(catalogue.rulesets)
        selected = [default] if default else []
    year_from = optional_int_param(params, "year_from", 1900, 2100)
    year_to = optional_int_param(params, "year_to", 1900, 2100)
    if year_from is None and selected:
        year_from = min(r.year_from for r in selected)
    if year_to is None and selected:
        year_to = max(r.year_to for r in selected)
    if year_from is not None and year_to is not None and year_from > year_to:
        raise InvalidParameter("year_from", "year_from must not be greater than year_to")
    country = tuple(code.upper() for code in items(params, "country"))
    for code in country:
        if not _COUNTRY.fullmatch(code):
            raise InvalidParameter("country", f"invalid country code {code}")
    return Filters(
        gender=gender,
        weight=weight,
        year_from=year_from,
        year_to=year_to,
        ruleset=tuple(r.id for r in selected),
        country=country,
        side=members(params, "side", SIDES),
        domain=members(params, "domain", DOMAINS),
        count_by=choice(params, "count_by", COUNT_BYS, "event"),
        min_scores_athlete=int_param(params, "min_scores_athlete", DEFAULT_MIN_SCORES_ATHLETE, 1, 50),
        min_scores_technique=int_param(params, "min_scores_technique", DEFAULT_MIN_SCORES_TECHNIQUE, 1, 10),
    )
