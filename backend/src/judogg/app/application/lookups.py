from judogg.app.application.errors import InvalidParameter, NotFound
from judogg.app.application.params import Params, text
from judogg.app.domain.model import Catalogue, Tag


def required(params: Params, name: str) -> str:
    value = text(params, name)
    if value is None:
        raise InvalidParameter(name, f"{name} is required")
    return value


def technique(catalogue: Catalogue, code: str, field: str) -> Tag:
    found = next((t for t in catalogue.tags.values() if t.code == code and t.kind == "technique"), None)
    if found is None:
        raise NotFound(field, f"unknown technique {code}")
    return found
