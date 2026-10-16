from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field

from judogg.app.domain.model import Direction, ScoreRow, ScoreValue
from judogg.app.domain.numbers import ratio

BIN_LABELS = (
    "0:00–0:30",
    "0:30–1:00",
    "1:00–1:30",
    "1:30–2:00",
    "2:00–2:30",
    "2:30–3:00",
    "3:00–3:30",
    "3:30–4:00",
    "Golden score",
)


def distinct(scores: Iterable[ScoreRow]) -> list[ScoreRow]:
    """A technique combination gives one row per technique but is one score: one row per (event, athlete)."""
    unique: dict[tuple[int, int], ScoreRow] = {}
    for score in scores:
        unique.setdefault((score.event_id, score.athlete_id), score)
    return list(unique.values())


@dataclass(frozen=True)
class TimingBin:
    bin: int
    label: str
    n: int
    ippon: int
    waza_ari: int
    yuko: int


def timing(scores: Iterable[ScoreRow]) -> tuple[TimingBin, ...]:
    per_bin = [Counter[ScoreValue]() for _ in BIN_LABELS]
    for score in scores:
        per_bin[score.time_bin][score.score_value] += 1
    return tuple(
        TimingBin(index, label, counts.total(), counts["ippon"], counts["waza_ari"], counts["yuko"])
        for index, (label, counts) in enumerate(zip(BIN_LABELS, per_bin, strict=True))
    )


@dataclass(frozen=True)
class ValueCounts:
    ippon: int
    waza_ari: int
    yuko: int


@dataclass(frozen=True)
class ValueShares:
    ippon: float | None
    waza_ari: float | None
    yuko: float | None


@dataclass(frozen=True)
class SideCounts:
    left: int
    right: int
    unknown: int


@dataclass
class TechniqueGroup:
    tag_id: int | None
    n: int = 0
    athletes: set[int] = field(default_factory=set)
    values: Counter[ScoreValue] = field(default_factory=Counter)
    sides: Counter[Direction] = field(default_factory=Counter)
    awasete: int = 0

    def counts(self) -> ValueCounts:
        return ValueCounts(self.values["ippon"], self.values["waza_ari"], self.values["yuko"])

    def shares(self) -> ValueShares:
        return ValueShares(
            ratio(self.values["ippon"], self.n),
            ratio(self.values["waza_ari"], self.n),
            ratio(self.values["yuko"], self.n),
        )

    def side_counts(self) -> SideCounts:
        return SideCounts(self.sides["left"], self.sides["right"], self.sides["unknown"])


def technique_groups(scores: Iterable[ScoreRow]) -> dict[int | None, TechniqueGroup]:
    groups: dict[int | None, TechniqueGroup] = {}
    for score in scores:
        group = groups.get(score.technique_tag_id)
        if group is None:
            group = groups[score.technique_tag_id] = TechniqueGroup(score.technique_tag_id)
        group.n += 1
        group.athletes.add(score.athlete_id)
        group.values[score.score_value] += 1
        group.sides[score.direction] += 1
        if score.is_awasete:
            group.awasete += 1
    return groups


def side_counts(scores: Iterable[ScoreRow]) -> SideCounts:
    sides = Counter(s.direction for s in scores)
    return SideCounts(sides["left"], sides["right"], sides["unknown"])
