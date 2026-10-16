"""Which competitions a download asks for. Exclusions by data (no events, few tags) need the download itself."""

import calendar
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from judogg.ingestion.domain.competitions import (
    ELITE_RANKS,
    ExclusionRules,
    exclusion_reason,
    parse_date,
    read_entry,
)
from judogg.ingestion.domain.constants import FIRST_YEAR
from judogg.ingestion.domain.model import RawJson


class InvalidSelection(ValueError):
    pass


@dataclass(frozen=True)
class Selection:
    years: frozenset[int] = frozenset()
    competition_ids: tuple[int, ...] = ()
    recent_months: int | None = None
    elite_only: bool = False

    @property
    def is_empty(self) -> bool:
        return not (self.years or self.competition_ids or self.recent_months)


@dataclass(frozen=True)
class Wanted:
    id: int
    name: str
    refresh: bool  # the IJF corrects results for months: recent competitions are downloaded again


def parse_years(text: str) -> frozenset[int]:
    """`2025`, `2025,2026` or `2020-2026`."""
    years: set[int] = set()
    for part in (p.strip() for p in text.split(",")):
        first, _, last = part.partition("-")
        try:
            start, end = int(first), int(last or first)
        except ValueError:
            raise InvalidSelection(f"{part!r} is not a year or a range of years") from None
        if start > end:
            raise InvalidSelection(f"{part}: the range goes backwards")
        if start < FIRST_YEAR:
            raise InvalidSelection(f"{start} is before {FIRST_YEAR}: older data is ignored")
        years.update(range(start, end + 1))
    return frozenset(years)


def months_before(day: date, months: int) -> date:
    """Calendar months; the day is clamped, so 31 May minus 3 months is the last day of February."""
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    month += 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def select_competitions(
    listing: Sequence[RawJson], selection: Selection, today: date, rules: ExclusionRules
) -> list[Wanted]:
    by_id = {read_entry(raw, lambda r: int(r["id_competition"])): raw for raw in listing}
    wanted = {competition_id: _explicit(by_id, competition_id) for competition_id in selection.competition_ids}
    since = months_before(today, selection.recent_months) if selection.recent_months else None
    for raw in listing:
        if not read_entry(raw, lambda r: _downloadable(r, today, rules, elite_only=selection.elite_only)):
            continue
        is_recent = since is not None and parse_date(raw["date_from"]) >= since
        if is_recent or int(raw["comp_year"]) in selection.years:
            competition_id = int(raw["id_competition"])
            wanted[competition_id] = Wanted(competition_id, str(raw["name"]), refresh=is_recent)
    return sorted(wanted.values(), key=lambda w: (parse_date(by_id[w.id]["date_from"]), w.id))


def category_weight_ids(payload: object) -> list[str]:
    """`competition.categories_full` maps each gender to its categories; any other shape has none."""
    if not isinstance(payload, dict):
        return []
    return [
        str(weight)
        for gender in payload.values()
        if isinstance(gender, dict)
        for weight in gender.get("categories") or {}
    ]


def _explicit(by_id: dict[int, RawJson], competition_id: int) -> Wanted:
    """Asked for by id: downloaded as asked, without the result, exclusion and end-date filters."""
    raw = by_id.get(competition_id)
    if raw is None:
        raise InvalidSelection(f"competition {competition_id} is not in the IJF competitions list")
    if read_entry(raw, lambda r: int(r["comp_year"])) < FIRST_YEAR:
        raise InvalidSelection(f"competition {competition_id} is from {raw['comp_year']}, before {FIRST_YEAR}")
    return Wanted(competition_id, str(raw["name"]), refresh=False)


def _downloadable(raw: RawJson, today: date, rules: ExclusionRules, *, elite_only: bool = False) -> bool:
    if elite_only and raw.get("rank_name") not in ELITE_RANKS:
        return False
    return (
        int(raw["comp_year"]) >= FIRST_YEAR
        and raw["has_results"] != "0"
        and exclusion_reason(str(raw["name"]), str(raw["rank_name"]), rules) is None
        and parse_date(raw["date_to"]) < today
    )
