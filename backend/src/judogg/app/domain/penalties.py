from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from judogg.app.domain.categories import selected_weights
from judogg.app.domain.model import WALKOVERS, Catalogue, ContestRow, EndType, Filters, PenaltyRow, Tag, Thresholds
from judogg.app.domain.numbers import Sample, count_sample, ratio
from judogg.app.domain.refs import ReasonRef, WeightRef, reason_ref, weight_ref
from judogg.app.domain.scores import BIN_LABELS

HANSOKU_END_TYPES: frozenset[EndType] = frozenset({"hansoku_shido", "double_hansoku"})
TOP_REASONS_PER_NUMBER = 5
UNKNOWN_GROUP = "Unknown group"


@dataclass(frozen=True)
class PenaltyKpis:
    n_penalties: int
    n_shido: int
    n_hansoku_shido: int
    played_contests: int
    shido_per_contest: float | None
    hansoku_share: float | None


@dataclass(frozen=True)
class ReasonRow:
    reason: ReasonRef | None
    n: int
    share: float | None
    n_deciding: int
    deciding_share: float | None
    sample: Sample


@dataclass(frozen=True)
class GroupRow:
    group_label: str | None
    n: int
    share: float | None


@dataclass(frozen=True)
class WeightPenalties:
    weight: WeightRef
    contests: int
    penalties: int
    shido_per_contest: float | None
    hansoku_share: float | None
    sample: Sample


@dataclass(frozen=True)
class PenaltyBin:
    bin: int
    label: str
    n: int


@dataclass(frozen=True)
class NumberReason:
    reason: ReasonRef | None
    n: int
    share: float | None


@dataclass(frozen=True)
class ShidoNumber:
    number: int
    n: int
    sample: Sample
    reasons: tuple[NumberReason, ...]


@dataclass(frozen=True)
class Penalties:
    kpis: PenaltyKpis
    sample: Sample
    reasons: tuple[ReasonRow, ...]
    by_group: tuple[GroupRow, ...]
    by_weight: tuple[WeightPenalties, ...]
    timing: tuple[PenaltyBin, ...]
    by_number: tuple[ShidoNumber, ...]


def build_penalties(
    penalties: Sequence[PenaltyRow],
    contests: Sequence[ContestRow],
    filters: Filters,
    catalogue: Catalogue,
    thresholds: Thresholds,
) -> Penalties:
    played = [c for c in contests if c.end_type not in WALKOVERS]
    played_ids = {c.id for c in played}
    in_played = [p for p in penalties if p.contest_id in played_ids]
    kinds = Counter(p.penalty_kind for p in penalties)
    kpis = PenaltyKpis(
        n_penalties=len(penalties),
        n_shido=kinds["shido"],
        n_hansoku_shido=kinds["hansoku_shido"],
        played_contests=len(played),
        shido_per_contest=ratio(len(in_played), len(played)),
        hansoku_share=ratio(sum(1 for c in played if c.end_type in HANSOKU_END_TYPES), len(played)),
    )
    bins = Counter(p.time_bin for p in penalties)
    return Penalties(
        kpis=kpis,
        sample=count_sample(len(penalties), thresholds, "penalties"),
        reasons=_reasons(penalties, catalogue.tags, thresholds),
        by_group=_groups(penalties, catalogue.tags),
        by_weight=_by_weight(played, in_played, filters, catalogue, thresholds),
        timing=tuple(PenaltyBin(index, label, bins[index]) for index, label in enumerate(BIN_LABELS)),
        by_number=tuple(_by_number(penalties, number, catalogue.tags, thresholds) for number in (1, 2, 3)),
    )


def _ordered_reasons(counts: Counter[int | None], tags: Mapping[int, Tag]) -> list[int | None]:
    """Most frequent first, ties by name; "no reason tagged" always last."""
    tagged = [r for r in counts if r is not None]
    tagged.sort(key=lambda r: tags[r].name)
    tagged.sort(key=lambda r: counts[r], reverse=True)
    return [*tagged, None] if None in counts else list(tagged)


def _ref(reason: int | None, tags: Mapping[int, Tag]) -> ReasonRef | None:
    return reason_ref(tags[reason]) if reason is not None else None


def _reasons(penalties: Sequence[PenaltyRow], tags: Mapping[int, Tag], thresholds: Thresholds) -> tuple[ReasonRow, ...]:
    counts = Counter(p.reason_tag_id for p in penalties)
    deciding = Counter(p.reason_tag_id for p in penalties if p.penalty_kind != "shido")
    return tuple(
        ReasonRow(
            reason=_ref(reason, tags),
            n=counts[reason],
            share=ratio(counts[reason], len(penalties)),
            n_deciding=deciding[reason],
            deciding_share=ratio(deciding[reason], counts[reason]),
            sample=count_sample(counts[reason], thresholds, "penalties"),
        )
        for reason in _ordered_reasons(counts, tags)
    )


def _groups(penalties: Sequence[PenaltyRow], tags: Mapping[int, Tag]) -> tuple[GroupRow, ...]:
    def label(reason: int | None) -> str | None:
        if reason is None:
            return None
        return tags[reason].group_label or UNKNOWN_GROUP

    counts = Counter(label(p.reason_tag_id) for p in penalties)
    labelled = [g for g in counts if g is not None]
    labelled.sort()
    labelled.sort(key=lambda g: counts[g], reverse=True)
    ordered = [*labelled, None] if None in counts else labelled
    return tuple(GroupRow(g, counts[g], ratio(counts[g], len(penalties))) for g in ordered)


def _by_weight(
    played: Sequence[ContestRow],
    in_played: Sequence[PenaltyRow],
    filters: Filters,
    catalogue: Catalogue,
    thresholds: Thresholds,
) -> tuple[WeightPenalties, ...]:
    rows = []
    for category in selected_weights(filters, catalogue.weights):
        contests = [c for c in played if c.weight == category.code]
        penalties = sum(1 for p in in_played if p.weight == category.code)
        hansoku = sum(1 for c in contests if c.end_type in HANSOKU_END_TYPES)
        rows.append(
            WeightPenalties(
                weight_ref(category),
                len(contests),
                penalties,
                ratio(penalties, len(contests)),
                ratio(hansoku, len(contests)),
                count_sample(len(contests), thresholds, "contests"),
            )
        )
    return tuple(rows)


def _by_number(
    penalties: Sequence[PenaltyRow], number: int, tags: Mapping[int, Tag], thresholds: Thresholds
) -> ShidoNumber:
    """A 4th or later penalty counts as the 3rd."""
    chosen = [p for p in penalties if min(p.shido_number, 3) == number]
    counts = Counter(p.reason_tag_id for p in chosen)
    reasons = _ordered_reasons(counts, tags)[:TOP_REASONS_PER_NUMBER]
    return ShidoNumber(
        number=number,
        n=len(chosen),
        sample=count_sample(len(chosen), thresholds, "penalties"),
        reasons=tuple(NumberReason(_ref(r, tags), counts[r], ratio(counts[r], len(chosen))) for r in reasons),
    )
