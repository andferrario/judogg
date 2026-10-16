from judogg.app.domain.model import Tag, WeightCategory
from judogg.app.domain.refs import ReasonRef, TechniqueRef, WeightRef, reason_ref, technique_ref, weight_ref


def test_references() -> None:
    throw = Tag(1, "seoi_nage", "Seoi-nage", "technique", "Te-waza", "standing")
    grip = Tag(2, "avoid_grip", "Avoid-grip", "shido_reason", "Grip", None)
    assert technique_ref(throw) == TechniqueRef("seoi_nage", "Seoi-nage", "Te-waza", "standing")
    assert reason_ref(grip) == ReasonRef("avoid_grip", "Avoid-grip", "Grip")


def test_weight_reference() -> None:
    assert weight_ref(WeightCategory("f+78", "f", "+78", 14)) == WeightRef("f+78", "f", "+78")
