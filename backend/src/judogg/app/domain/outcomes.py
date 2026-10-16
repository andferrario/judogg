from collections.abc import Sequence
from dataclasses import dataclass

from judogg.app.domain.categories import selected_weights
from judogg.app.domain.model import WALKOVERS, Catalogue, ContestRow, Filters, PenaltyRow, Thresholds
from judogg.app.domain.numbers import ratio
from judogg.app.domain.overview import Outcomes, outcomes
from judogg.app.domain.refs import WeightRef, weight_ref


@dataclass(frozen=True)
class OutcomesWithShido(Outcomes):
    shido_per_contest: float | None


@dataclass(frozen=True)
class WeightOutcomes(OutcomesWithShido):
    weight: WeightRef


@dataclass(frozen=True)
class OutcomeTable:
    rows: tuple[WeightOutcomes, ...]
    total: OutcomesWithShido


def _with_shido(
    contests: Sequence[ContestRow], penalties: Sequence[PenaltyRow], thresholds: Thresholds
) -> OutcomesWithShido:
    base = outcomes(contests, thresholds)
    played = {c.id for c in contests if c.end_type not in WALKOVERS}
    shido = ratio(sum(1 for p in penalties if p.contest_id in played), base.played)
    return OutcomesWithShido(
        base.played, base.walkovers, base.end_types, base.gs_share, base.avg_duration_s, base.sample, shido
    )


def build_outcome_table(
    contests: Sequence[ContestRow],
    penalties: Sequence[PenaltyRow],
    filters: Filters,
    catalogue: Catalogue,
    thresholds: Thresholds,
) -> OutcomeTable:
    rows = []
    for category in selected_weights(filters, catalogue.weights):
        own = _with_shido(
            [c for c in contests if c.weight == category.code],
            [p for p in penalties if p.weight == category.code],
            thresholds,
        )
        rows.append(
            WeightOutcomes(
                own.played,
                own.walkovers,
                own.end_types,
                own.gs_share,
                own.avg_duration_s,
                own.sample,
                own.shido_per_contest,
                weight_ref(category),
            )
        )
    return OutcomeTable(tuple(rows), _with_shido(contests, penalties, thresholds))
