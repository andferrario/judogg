from collections.abc import Collection
from typing import Protocol

from judogg.app.domain.model import (
    Athlete,
    Catalogue,
    ContestRow,
    Filters,
    IssueRow,
    PenaltyRow,
    ScoreRow,
    TableCounts,
)


class DatasetReader(Protocol):
    def catalogue(self) -> Catalogue: ...

    def scores(self, filters: Filters | None) -> list[ScoreRow]: ...

    def contests(self, filters: Filters | None) -> list[ContestRow]: ...

    def penalties(self, filters: Filters | None) -> list[PenaltyRow]: ...

    def table_counts(self) -> TableCounts: ...

    def quality_issues(self) -> list[IssueRow]: ...

    def athletes(self, ids: Collection[int] | None) -> dict[int, Athlete]: ...

    def search_athletes(self, term: str) -> list[Athlete]: ...

    def contests_of_athletes(self, ids: Collection[int]) -> list[ContestRow]: ...

    def scores_of_athletes(self, ids: Collection[int]) -> list[ScoreRow]: ...
