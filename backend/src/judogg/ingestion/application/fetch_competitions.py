from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from judogg.ingestion.application.errors import CallFailed, FetchError
from judogg.ingestion.application.ports import Clock, IjfClient, RawResponseRepository
from judogg.ingestion.application.raw_responses import (
    CATEGORIES,
    COMPETITION_LIST,
    CONTEST_PARTS,
    CONTESTS,
    RawResponse,
)
from judogg.ingestion.domain.competitions import ExclusionRules, InvalidCompetitionEntry, is_competition_list
from judogg.ingestion.domain.selection import (
    InvalidSelection,
    Selection,
    Wanted,
    category_weight_ids,
    select_competitions,
)


@dataclass(frozen=True)
class FetchSummary:
    competitions: int
    downloaded: int
    skipped: int
    failed: tuple[str, ...]  # "<endpoint> <params>: <reason>"


@dataclass
class _Tally:
    downloaded: int = 0
    skipped: int = 0
    failed: list[str] = field(default_factory=list)

    def counts(self) -> tuple[int, int, int]:
        return self.downloaded, self.skipped, len(self.failed)


class FetchCompetitions:
    """Writes raw responses only: `load` turns them into the app tables."""

    def __init__(
        self,
        client: IjfClient,
        raw: RawResponseRepository,
        clock: Clock,
        rules: ExclusionRules,
        progress: Callable[[str], None],
    ) -> None:
        self._client = client
        self._raw = raw
        self._clock = clock
        self._rules = rules
        self._progress = progress

    def execute(self, selection: Selection, *, force: bool) -> FetchSummary:
        tally = _Tally()
        listing = self._call(tally, COMPETITION_LIST, {}, refresh=True, is_list=True)
        if listing is None:
            return _summary(0, tally)
        try:
            wanted = select_competitions(listing, selection, self._clock.today(), self._rules)
        except (InvalidSelection, InvalidCompetitionEntry) as error:
            raise FetchError(str(error)) from error
        for competition in wanted:
            self._competition(tally, competition, refresh=force or competition.refresh)
        return _summary(len(wanted), tally)

    def _competition(self, tally: _Tally, competition: Wanted, *, refresh: bool) -> None:
        before = tally.counts()
        competition_id = str(competition.id)
        categories = self._call(tally, CATEGORIES, {"id_competition": competition_id}, refresh)
        for weight in category_weight_ids(categories):
            params = {"id_competition": competition_id, "id_weight": weight, "part": CONTEST_PARTS}
            self._call(tally, CONTESTS, params, refresh)
        downloaded, skipped, failed = (now - then for now, then in zip(tally.counts(), before, strict=True))
        self._progress(
            f"{competition.id} {competition.name}: {downloaded} downloaded, {skipped} skipped, {failed} failed"
        )

    def _call(
        self,
        tally: _Tally,
        endpoint: str,
        params: Mapping[str, str],
        refresh: bool,
        *,
        is_list: bool = False,
    ) -> Any | None:
        if not refresh:
            stored = self._raw.get(endpoint, params)
            if stored is not None:
                tally.skipped += 1
                return stored
        try:
            payload = self._client.get(endpoint, params)
        except CallFailed as error:
            tally.failed.append(f"{endpoint} {dict(params)}: {error}")
            return None
        if is_list and not is_competition_list(payload):
            tally.failed.append(f"{endpoint} {dict(params)}: the answer is not a competitions list")
            return None
        self._raw.save(RawResponse(endpoint, params, payload))
        tally.downloaded += 1
        return payload


def _summary(competitions: int, tally: _Tally) -> FetchSummary:
    return FetchSummary(competitions, tally.downloaded, tally.skipped, tuple(tally.failed))
