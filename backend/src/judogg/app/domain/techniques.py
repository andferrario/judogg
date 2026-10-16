from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from judogg.app.domain.model import CountBy, ScoreRow, Tag, Thresholds
from judogg.app.domain.numbers import Sample, count_sample, ratio
from judogg.app.domain.refs import TechniqueRef, technique_ref
from judogg.app.domain.scores import SideCounts, TechniqueGroup, ValueCounts, ValueShares, distinct, technique_groups

SortKey = Literal["share", "n_scores", "n_athletes", "pct_ippon", "pct_waza_ari", "pct_yuko"]
SortOrder = Literal["asc", "desc"]
SORT_KEYS: tuple[SortKey, ...] = ("share", "n_scores", "n_athletes", "pct_ippon", "pct_waza_ari", "pct_yuko")
SORT_ORDERS: tuple[SortOrder, ...] = ("asc", "desc")


@dataclass(frozen=True)
class TierRow:
    technique: TechniqueRef | None
    n_scores: int
    n_athletes: int
    share: float | None
    counts: ValueCounts
    pct: ValueShares
    n_awasete: int
    side: SideCounts
    sample: Sample


@dataclass(frozen=True)
class TierList:
    rows: tuple[TierRow, ...]
    total_rows: int
    sort: SortKey
    order: SortOrder
    sample: Sample


def build_tier_list(
    scores: Sequence[ScoreRow],
    tags: Mapping[int, Tag],
    count_by: CountBy,
    sort: SortKey,
    order: SortOrder,
    limit: int,
    thresholds: Thresholds,
) -> TierList:
    unique = distinct(scores)
    scoring_athletes = len({s.athlete_id for s in unique})
    rows = [
        _row(group, tags, count_by, len(unique), scoring_athletes, thresholds)
        for group in technique_groups(scores).values()
    ]
    known = [r for r in rows if r.technique is not None]
    known.sort(key=_name)
    known.sort(key=lambda r: r.n_scores, reverse=True)
    known.sort(key=lambda r: _sort_value(r, sort), reverse=order == "desc")
    ordered = known + [r for r in rows if r.technique is None]
    return TierList(tuple(ordered[:limit]), len(ordered), sort, order, count_sample(len(unique), thresholds))


def _row(
    group: TechniqueGroup,
    tags: Mapping[int, Tag],
    count_by: CountBy,
    distinct_scores: int,
    scoring_athletes: int,
    thresholds: Thresholds,
) -> TierRow:
    share = ratio(group.n, distinct_scores) if count_by == "event" else ratio(len(group.athletes), scoring_athletes)
    return TierRow(
        technique=technique_ref(tags[group.tag_id]) if group.tag_id is not None else None,
        n_scores=group.n,
        n_athletes=len(group.athletes),
        share=share,
        counts=group.counts(),
        pct=group.shares(),
        n_awasete=group.awasete,
        side=group.side_counts(),
        sample=count_sample(group.n, thresholds),
    )


def _name(row: TierRow) -> str:
    return row.technique.name if row.technique else ""


def _sort_value(row: TierRow, sort: SortKey) -> float:
    values: dict[SortKey, float | None] = {
        "share": row.share,
        "n_scores": row.n_scores,
        "n_athletes": row.n_athletes,
        "pct_ippon": row.pct.ippon,
        "pct_waza_ari": row.pct.waza_ari,
        "pct_yuko": row.pct.yuko,
    }
    value = values[sort]
    return value if value is not None else 0.0
