from dataclasses import dataclass

from judogg.app.domain.envelope import Totals, WarningItem
from judogg.app.domain.model import Filters


@dataclass(frozen=True)
class Filtered[T]:
    filters: Filters
    totals: Totals
    warnings: tuple[WarningItem, ...]
    data: T
