from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from judogg.app.domain.categories import most_frequent_weight
from judogg.app.domain.model import ScoreRow, Tag
from judogg.app.domain.scores import distinct


@dataclass
class AthleteProfile:
    id: int
    total: int = 0
    techniques: Counter[int] = field(default_factory=Counter)
    ippons: Counter[int] = field(default_factory=Counter)
    weights: Counter[str] = field(default_factory=Counter)
    main: int | None = None
    weight: str = ""


def main_technique(counts: Mapping[int, int], ippons: Mapping[int, int], tags: Mapping[int, Tag]) -> int | None:
    if not counts:
        return None
    return min(counts, key=lambda tag_id: (-counts[tag_id], -ippons.get(tag_id, 0), tags[tag_id].code))


def athlete_profiles(
    scores: Sequence[ScoreRow], tags: Mapping[int, Tag], sort_order: Mapping[str, int]
) -> dict[int, AthleteProfile]:
    """Per athlete: distinct scores (unknown technique included), technique rows, main technique and category."""
    profiles: dict[int, AthleteProfile] = {}
    for score in distinct(scores):
        profile = profiles.get(score.athlete_id)
        if profile is None:
            profile = profiles[score.athlete_id] = AthleteProfile(score.athlete_id)
        profile.total += 1
        profile.weights[score.weight] += 1
    for score in scores:
        if score.technique_tag_id is None:
            continue
        profile = profiles[score.athlete_id]
        profile.techniques[score.technique_tag_id] += 1
        if score.score_value == "ippon":
            profile.ippons[score.technique_tag_id] += 1
    for profile in profiles.values():
        profile.main = main_technique(profile.techniques, profile.ippons, tags)
        profile.weight = most_frequent_weight(profile.weights, sort_order)
    return profiles
