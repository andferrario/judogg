import pytest
from ijf_helpers import (
    FUSEN_GACHI,
    KESA_GATAME,
    LEFT,
    NEW_GROUP_REASON,
    NEW_GROUP_TECHNIQUE,
    NON_COMBATIVITY,
    OSAEKOMI,
    RIGHT,
    SEOI_NAGE,
)

from judogg.ingestion.domain.model import Tag
from judogg.ingestion.domain.tags import direction, tag_kind, technique_domain, to_tag


def test_tag_kind_from_id_groups() -> None:
    assert tag_kind(SEOI_NAGE) == "technique"
    assert tag_kind(KESA_GATAME) == "technique"
    assert tag_kind(NON_COMBATIVITY) == "shido_reason"
    assert tag_kind(LEFT) is None
    assert tag_kind(FUSEN_GACHI) is None
    assert tag_kind(OSAEKOMI) is None


def test_to_tag_labels_and_normalises() -> None:
    assert to_tag(SEOI_NAGE) == Tag(1, "seoi_nage", "Seoi-nage", "technique", "Te-waza", "standing")
    assert to_tag(KESA_GATAME) == Tag(3, "kesa_gatame", "Kesa-gatame", "technique", "Osaekomi-waza", "ground")
    assert to_tag(NON_COMBATIVITY) == Tag(5, "non_combativity", "Non-combativity", "shido_reason", "Passivity", None)


def test_to_tag_with_an_unknown_group_has_no_label() -> None:
    assert to_tag(NEW_GROUP_TECHNIQUE) == Tag(4, "new_throw", "New-throw", "technique", None, None)
    assert to_tag(NEW_GROUP_REASON) == Tag(6, "new_reason", "New-reason", "shido_reason", None, None)


def test_to_tag_rejects_tags_that_are_not_stored() -> None:
    with pytest.raises(ValueError, match="left"):
        to_tag(LEFT)


def test_technique_domain() -> None:
    assert technique_domain(SEOI_NAGE) == "standing"
    assert technique_domain(KESA_GATAME) == "ground"
    assert technique_domain(NEW_GROUP_TECHNIQUE) == "unknown"


def test_direction_from_the_side_tag() -> None:
    assert direction([SEOI_NAGE, LEFT]) == "left"
    assert direction([RIGHT]) == "right"
    assert direction([SEOI_NAGE]) == "unknown"
    assert direction([{**LEFT, "code_short": "both"}]) == "unknown"


@pytest.mark.parametrize("field", ["code_short", "name"])
def test_tag_without_code_or_name_is_an_error(field: str) -> None:
    with pytest.raises(ValueError, match=field):
        to_tag({**SEOI_NAGE, field: None})
