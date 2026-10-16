from dataclasses import dataclass
from typing import Literal

from judogg.app.domain.model import Gender, Tag, WeightCategory


@dataclass(frozen=True)
class TechniqueRef:
    code: str
    name: str
    group_label: str | None
    domain: Literal["standing", "ground"] | None


@dataclass(frozen=True)
class ReasonRef:
    code: str
    name: str
    group_label: str | None


def technique_ref(tag: Tag) -> TechniqueRef:
    return TechniqueRef(tag.code, tag.name, tag.group_label, tag.domain)


def reason_ref(tag: Tag) -> ReasonRef:
    return ReasonRef(tag.code, tag.name, tag.group_label)


@dataclass(frozen=True)
class WeightRef:
    code: str
    gender: Gender
    label: str


def weight_ref(category: WeightCategory) -> WeightRef:
    return WeightRef(category.code, category.gender, category.label)
