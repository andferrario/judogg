import re
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date

from judogg.ingestion.domain.constants import FIRST_YEAR
from judogg.ingestion.domain.model import Competition, Level, RawJson, Ruleset, RulesetKey

ELITE_RANKS = frozenset(
    {
        "Olympic Games",
        "World Championships",
        "Masters",
        "Grand Slam",
        "Grand Prix",
        "European Championships",
        "Asian Championships",
        "African Championships",
        "Panamerica Championships",
        "Oceanian Championships",
    }
)


class InvalidCompetitionEntry(ValueError):
    pass


class RulesetConflict(Exception):
    """Two rulesets starting in the same year would share the same id."""


@dataclass(frozen=True)
class ExclusionRules:
    ranks: frozenset[str]
    name_patterns: tuple[tuple[re.Pattern[str], str], ...]


def is_competition_list(payload: object) -> bool:
    """Every load starts from this list: an IJF error page in JSON must never replace it."""
    return isinstance(payload, list) and all(isinstance(raw, dict) and "id_competition" in raw for raw in payload)


def exclusion_reason(name: str, rank_name: str, rules: ExclusionRules) -> str | None:
    if rank_name in rules.ranks:
        return f"rank_name {rank_name}"
    return next((reason for pattern, reason in rules.name_patterns if pattern.search(name)), None)


def competition_level(rank_name: str) -> Level:
    return "elite" if rank_name in ELITE_RANKS else "continental"


def ruleset_key(raw: RawJson) -> RulesetKey:
    max_wazaari = raw["max_wazaari"]
    return RulesetKey(
        has_koka=raw["has_koka"] == "1",
        has_yuko=raw["has_yuko"] == "1",
        max_wazaari=int(max_wazaari) if max_wazaari is not None else None,
        max_shido=int(raw["max_shido"]),
    )


def derive_rulesets(raws: Sequence[RawJson]) -> list[Ruleset]:
    """One ruleset per distinct combination; id = first year, so URLs stay stable across loads."""
    years: dict[RulesetKey, list[int]] = defaultdict(list)
    for raw in raws:
        key, year = read_entry(raw, lambda r: (ruleset_key(r), int(r["comp_year"])))
        years[key].append(year)
    ordered = sorted(years, key=lambda key: min(years[key]))
    first_years = [min(years[key]) for key in ordered]
    if len(set(first_years)) != len(first_years):
        raise RulesetConflict(f"two rulesets start in the same year: {first_years}")
    rulesets = []
    for index, key in enumerate(ordered):
        year_from, year_to = min(years[key]), max(years[key])
        if index == len(ordered) - 1:
            label = f"{year_from}–"
        elif year_from == year_to:
            label = str(year_from)
        else:
            label = f"{year_from}–{year_to}"
        rulesets.append(Ruleset(year_from, key, year_from, year_to, label))
    return rulesets


def build_competitions(raws: Sequence[RawJson], rules: ExclusionRules) -> tuple[list[Competition], list[Ruleset]]:
    """Scheduled competitions are included: they extend the years of the current ruleset."""
    recent = [raw for raw in raws if read_entry(raw, lambda r: int(r["comp_year"])) >= FIRST_YEAR]
    rulesets = derive_rulesets(recent)
    ruleset_ids = {ruleset.key: ruleset.id for ruleset in rulesets}
    competitions = [read_entry(raw, lambda r: _competition(r, ruleset_ids, rules)) for raw in recent]
    return sorted(competitions, key=lambda c: c.id), rulesets


def _competition(raw: RawJson, ruleset_ids: dict[RulesetKey, int], rules: ExclusionRules) -> Competition:
    name, rank_name = _text(raw, "name"), _text(raw, "rank_name")
    return Competition(
        id=int(raw["id_competition"]),
        code=str(raw["competition_code"]) if raw.get("competition_code") else None,
        name=name,
        rank_name=rank_name,
        date_from=parse_date(raw["date_from"]),
        date_to=parse_date(raw["date_to"]),
        year=int(raw["comp_year"]),
        ruleset_id=ruleset_ids[ruleset_key(raw)],
        level=competition_level(rank_name),
        exclusion_reason=exclusion_reason(name, rank_name, rules),
    )


def _text(raw: RawJson, key: str) -> str:
    value = raw[key]
    if value is None:
        raise ValueError(f"{key} is null")
    return str(value)


def read_entry[T](raw: RawJson, convert: Callable[[RawJson], T]) -> T:
    try:
        return convert(raw)
    except (KeyError, TypeError, ValueError) as error:
        raise InvalidCompetitionEntry(f"competition {raw.get('id_competition')}: {error!r}") from error


def parse_date(value: object) -> date:
    year, month, day = (int(part) for part in str(value).split("/"))
    return date(year, month, day)
