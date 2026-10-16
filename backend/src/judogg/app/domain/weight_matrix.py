from collections.abc import Sequence
from dataclasses import dataclass

from judogg.app.domain.categories import selected_weights
from judogg.app.domain.model import Catalogue, Filters, ScoreRow, Thresholds
from judogg.app.domain.numbers import Sample, count_sample, ratio
from judogg.app.domain.refs import TechniqueRef, WeightRef, technique_ref, weight_ref
from judogg.app.domain.scores import distinct, technique_groups


@dataclass(frozen=True)
class Cell:
    technique: str
    n: int
    share: float | None


@dataclass(frozen=True)
class WeightRow:
    weight: WeightRef
    total: int
    sample: Sample
    cells: tuple[Cell, ...]


@dataclass(frozen=True)
class WeightMatrix:
    techniques: tuple[TechniqueRef, ...]
    rows: tuple[WeightRow, ...]


def build_weight_matrix(
    scores: Sequence[ScoreRow], filters: Filters, catalogue: Catalogue, top: int, thresholds: Thresholds
) -> WeightMatrix:
    by_athlete = filters.count_by == "athlete"
    ranking = [g for g in technique_groups(scores).values() if g.tag_id is not None]
    ranking.sort(key=lambda g: catalogue.tags[g.tag_id].name if g.tag_id is not None else "")
    ranking.sort(key=lambda g: g.n, reverse=True)
    ranking.sort(key=lambda g: len(g.athletes) if by_athlete else g.n, reverse=True)
    chosen = [catalogue.tags[g.tag_id] for g in ranking[:top] if g.tag_id is not None]
    rows = []
    for category in selected_weights(filters, catalogue.weights):
        in_weight = [s for s in scores if s.weight == category.code]
        unique = distinct(in_weight)
        total = len({s.athlete_id for s in unique}) if by_athlete else len(unique)
        cells = []
        for tag in chosen:
            with_tag = [s for s in in_weight if s.technique_tag_id == tag.id]
            n = len({s.athlete_id for s in with_tag}) if by_athlete else len(with_tag)
            cells.append(Cell(tag.code, n, ratio(n, total)))
        rows.append(WeightRow(weight_ref(category), total, count_sample(len(unique), thresholds), tuple(cells)))
    return WeightMatrix(tuple(technique_ref(t) for t in chosen), tuple(rows))
