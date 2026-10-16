from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Literal

from judogg.app.domain.model import ContestRow, Filters, PenaltyRow, Ruleset, ScoreRow, Thresholds
from judogg.app.domain.numbers import rounded_percent
from judogg.app.domain.scores import distinct

WarningCode = Literal["mixed_score_scales", "high_unknown_technique", "quality_issues"]


@dataclass(frozen=True)
class Totals:
    competitions: int
    contests: int
    athletes: int
    scores: int
    penalties: int


@dataclass(frozen=True)
class WarningItem:
    code: WarningCode
    message: str


def totals(scores: Iterable[ScoreRow], contests: Sequence[ContestRow], penalties: Sequence[PenaltyRow]) -> Totals:
    return Totals(
        competitions=len({c.competition_id for c in contests}),
        contests=len(contests),
        athletes=len({athlete for c in contests for athlete in (c.white_athlete_id, c.blue_athlete_id)}),
        scores=len(distinct(scores)),
        penalties=len(penalties),
    )


def warnings(
    filters: Filters,
    rulesets: Iterable[Ruleset],
    scores: Sequence[ScoreRow] | None,
    contests: Sequence[ContestRow],
    thresholds: Thresholds,
) -> tuple[WarningItem, ...]:
    """`scores` is None on the endpoints that do not analyse scores."""
    found = []
    scales = {(r.has_koka, r.has_yuko) for r in rulesets if r.id in filters.ruleset and r.contests}
    if len(scales) > 1:
        found.append(
            WarningItem(
                "mixed_score_scales",
                "The selected rulesets have different score scales: ippon/waza-ari/yuko shares are not comparable.",
            )
        )
    if scores is not None:
        unique = distinct(scores)
        unknown = sum(1 for s in unique if s.technique_tag_id is None)
        if unique and unknown / len(unique) > thresholds.unknown_technique_warning:
            percent = rounded_percent(unknown, len(unique))
            found.append(WarningItem("high_unknown_technique", f"{percent}% of the scores have no technique."))
    flagged = sum(1 for c in contests if c.has_quality_issue)
    if flagged == 1:
        found.append(WarningItem("quality_issues", "1 contest in the filter has inconsistent IJF data."))
    elif flagged:
        found.append(WarningItem("quality_issues", f"{flagged} contests in the filter have inconsistent IJF data."))
    return tuple(found)
