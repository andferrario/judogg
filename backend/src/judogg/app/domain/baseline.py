from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from judogg.app.domain.model import ScoreRow
from judogg.app.domain.scores import distinct


@dataclass(frozen=True)
class CategoryShares:
    totals: Mapping[str, int]
    counts: Mapping[tuple[str, int | None], int]


def category_shares(scores: Sequence[ScoreRow]) -> CategoryShares:
    totals = Counter(s.weight for s in distinct(scores))
    counts = Counter((s.weight, s.technique_tag_id) for s in scores)
    return CategoryShares(totals, counts)


def expected_share(shares: CategoryShares, weights: Mapping[str, int], total: int, technique: int | None) -> float:
    """The share a technique would have with these athletes' category mix: lifts compare with it, so that a lift
    measures the technique and not the categories."""
    expected = 0.0
    for weight, n in weights.items():
        category_total = shares.totals.get(weight, 0)
        if category_total:
            expected += n / total * shares.counts.get((weight, technique), 0) / category_total
    return expected
