from collections.abc import Mapping, Sequence

from judogg.app.domain.model import Filters, WeightCategory


def selected_weights(filters: Filters, weights: Sequence[WeightCategory]) -> list[WeightCategory]:
    if filters.weight:
        chosen = set(filters.weight)
        return [w for w in weights if w.code in chosen]
    return [w for w in weights if filters.gender in ("all", w.gender)]


def sort_orders(weights: Sequence[WeightCategory]) -> dict[str, int]:
    return {w.code: w.sort_order for w in weights}


def most_frequent_weight(counts: Mapping[str, int], sort_order: Mapping[str, int]) -> str:
    return min(counts, key=lambda code: (-counts[code], sort_order[code]))
