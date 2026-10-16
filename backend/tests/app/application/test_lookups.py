import pytest
from app_fakes import catalogue

from judogg.app.application.errors import InvalidParameter, NotFound
from judogg.app.application.lookups import required, technique
from judogg.app.domain.model import Tag

TAGS = {
    1: Tag(1, "seoi_nage", "Seoi-nage", "technique", "Te-waza", "standing"),
    2: Tag(2, "non_combativity", "Non-combativity", "shido_reason", "Passivity", None),
}


def test_technique_lookup() -> None:
    assert technique(catalogue(tags=TAGS), "seoi_nage", "technique").id == 1


@pytest.mark.parametrize("code", ["nope", "non_combativity"])
def test_unknown_or_non_technique_codes_are_not_found(code: str) -> None:
    with pytest.raises(NotFound) as error:
        technique(catalogue(tags=TAGS), code, "with")
    assert error.value.field == "with"


def test_required_parameter() -> None:
    assert required({"technique": "seoi_nage"}, "technique") == "seoi_nage"
    with pytest.raises(InvalidParameter) as error:
        required({"technique": ""}, "technique")
    assert error.value.field == "technique"
