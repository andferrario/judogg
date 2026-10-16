from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from datetime import date
from typing import Any

from judogg.ingestion.application.errors import CallFailed
from judogg.ingestion.application.raw_responses import CONTESTS, RawResponse, params_hash
from judogg.ingestion.domain.model import Competition, Inclusion, ParsedContest, QualityIssue, Ruleset


class FakeRawResponses:
    def __init__(self, responses: Sequence[RawResponse] = ()) -> None:
        self.rows: dict[tuple[str, str], RawResponse] = {}
        for response in responses:
            self.save(response)

    def save(self, response: RawResponse) -> None:
        self.rows[(response.endpoint, params_hash(response.params))] = response

    def get(self, endpoint: str, params: Mapping[str, str]) -> Any | None:
        response = self.rows.get((endpoint, params_hash(params)))
        return response.payload if response else None

    def contest_competition_ids(self) -> list[int]:
        return sorted({r.competition_id for r in self.rows.values() if r.endpoint == CONTESTS and r.competition_id})

    def contest_payloads(self, competition_id: int) -> Iterator[Any]:
        yield from (
            r.payload for r in self.rows.values() if r.endpoint == CONTESTS and r.competition_id == competition_id
        )


class FakeWriter:
    def __init__(self) -> None:
        self.rulesets: list[Ruleset] = []
        self.competitions: list[Competition] = []
        self.inclusions: dict[int, Inclusion] = {}
        self.contests: list[ParsedContest] = []
        self.issues: list[QualityIssue] = []

    def add_rulesets(self, rulesets: Sequence[Ruleset]) -> None:
        self.rulesets += rulesets

    def add_competitions(self, competitions: Sequence[Competition]) -> None:
        self.competitions += competitions

    def set_inclusion(self, competition_id: int, inclusion: Inclusion) -> None:
        self.inclusions[competition_id] = inclusion

    def add_contests(self, contests: Sequence[ParsedContest]) -> None:
        self.contests += contests

    def add_issues(self, issues: Sequence[QualityIssue]) -> None:
        self.issues += issues


class FakeDataset:
    def __init__(self) -> None:
        self.writer: FakeWriter | None = None

    @contextmanager
    def rebuild(self) -> Iterator[FakeWriter]:
        writer = FakeWriter()
        yield writer
        self.writer = writer  # "committed" only when the block ends without an exception

    def table_counts(self) -> dict[str, int]:
        return {"contest": len(self.writer.contests) if self.writer else 0}


class FakeIjfClient:
    """Answers with stored responses; any other call fails, as a 404 would."""

    def __init__(self, responses: Sequence[RawResponse], failing: Sequence[tuple[str, Mapping[str, str]]] = ()) -> None:
        self.payloads = {(r.endpoint, params_hash(r.params)): r.payload for r in responses}
        self.failing = {(endpoint, params_hash(params)) for endpoint, params in failing}
        self.calls: list[tuple[str, dict[str, str]]] = []

    def get(self, endpoint: str, params: Mapping[str, str]) -> Any:
        self.calls.append((endpoint, dict(params)))
        key = (endpoint, params_hash(params))
        if key in self.failing or key not in self.payloads:
            raise CallFailed("HTTP 404")
        return self.payloads[key]

    def close(self) -> None:
        pass


class FixedClock:
    def __init__(self, day: date) -> None:
        self.day = day

    def today(self) -> date:
        return self.day
