from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from judogg.app.domain.model import WALKOVERS, ContestRow, EndType, ScoreRow, Thresholds
from judogg.app.domain.numbers import Sample, count_sample, ratio, rounded_mean
from judogg.app.domain.scores import TimingBin, distinct, timing

FOUGHT_END_TYPES: tuple[EndType, ...] = (
    "ippon",
    "waza_ari_awasete",
    "hansoku_shido",
    "double_hansoku",
    "score_gs",
    "score_regulation",
)


@dataclass(frozen=True)
class Walkovers:
    fusen_gachi: int
    kiken_gachi: int


@dataclass(frozen=True)
class EndTypeCount:
    end_type: EndType
    n: int
    share: float | None


@dataclass(frozen=True)
class Outcomes:
    played: int
    walkovers: Walkovers
    end_types: tuple[EndTypeCount, ...]
    gs_share: float | None
    avg_duration_s: int | None
    sample: Sample


@dataclass(frozen=True)
class OverviewKpis:
    scores: int
    contests: int
    scoring_athletes: int
    techniques: int
    gs_share: float | None
    unknown_side_share: float | None
    unknown_technique_share: float | None


@dataclass(frozen=True)
class Overview:
    kpis: OverviewKpis
    outcomes: Outcomes
    timing: tuple[TimingBin, ...]
    sample: Sample


def outcomes(contests: Sequence[ContestRow], thresholds: Thresholds) -> Outcomes:
    fought = [c for c in contests if c.end_type not in WALKOVERS]
    ends = Counter(c.end_type for c in contests)
    return Outcomes(
        played=len(fought),
        walkovers=Walkovers(ends["fusen_gachi"], ends["kiken_gachi"]),
        end_types=tuple(EndTypeCount(end, ends[end], ratio(ends[end], len(fought))) for end in FOUGHT_END_TYPES),
        gs_share=ratio(sum(1 for c in fought if c.went_gs), len(fought)),
        avg_duration_s=rounded_mean(sum(c.duration_s for c in fought), len(fought)),
        sample=count_sample(len(fought), thresholds, "contests"),
    )


def build_overview(scores: Sequence[ScoreRow], contests: Sequence[ContestRow], thresholds: Thresholds) -> Overview:
    unique = distinct(scores)
    result = outcomes(contests, thresholds)
    kpis = OverviewKpis(
        scores=len(unique),
        contests=len(contests),
        scoring_athletes=len({s.athlete_id for s in unique}),
        techniques=len({s.technique_tag_id for s in scores if s.technique_tag_id is not None}),
        gs_share=result.gs_share,
        unknown_side_share=ratio(sum(1 for s in unique if s.direction == "unknown"), len(unique)),
        unknown_technique_share=ratio(sum(1 for s in unique if s.technique_tag_id is None), len(unique)),
    )
    return Overview(kpis, result, timing(unique), count_sample(len(unique), thresholds))
