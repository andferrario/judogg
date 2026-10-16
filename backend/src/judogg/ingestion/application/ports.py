from collections.abc import Iterator, Mapping, Sequence
from contextlib import AbstractContextManager
from datetime import date
from typing import Any, Protocol

from judogg.ingestion.application.raw_responses import RawResponse
from judogg.ingestion.domain.model import Competition, Inclusion, ParsedContest, QualityIssue, Ruleset


class RawResponseRepository(Protocol):
    def save(self, response: RawResponse) -> None: ...

    def get(self, endpoint: str, params: Mapping[str, str]) -> Any | None: ...

    def contest_competition_ids(self) -> list[int]: ...

    def contest_payloads(self, competition_id: int) -> Iterator[Any]: ...


class DatasetWriter(Protocol):
    def add_rulesets(self, rulesets: Sequence[Ruleset]) -> None: ...

    def add_competitions(self, competitions: Sequence[Competition]) -> None: ...

    def set_inclusion(self, competition_id: int, inclusion: Inclusion) -> None: ...

    def add_contests(self, contests: Sequence[ParsedContest]) -> None: ...

    def add_issues(self, issues: Sequence[QualityIssue]) -> None: ...


class DatasetRepository(Protocol):
    def rebuild(self) -> AbstractContextManager[DatasetWriter]:
        """Empties the app tables and returns a writer; everything is committed together, or nothing."""
        ...

    def table_counts(self) -> dict[str, int]: ...


class IjfClient(Protocol):
    def get(self, endpoint: str, params: Mapping[str, str]) -> Any:
        """The decoded JSON answer; raises CallFailed when the call still fails after its retries."""
        ...


class Clock(Protocol):
    def today(self) -> date: ...
