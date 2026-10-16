from typing import Any

from judogg.app.interfaces.api.main import create_app

SCHEMA: dict[str, Any] = create_app().openapi()


def test_every_field_is_required_even_when_nullable() -> None:
    for name, schema in SCHEMA["components"]["schemas"].items():
        assert set(schema.get("required", [])) == set(schema.get("properties", {})), name


def test_errors_are_documented_with_the_error_body_and_never_as_422() -> None:
    for path, operations in SCHEMA["paths"].items():
        responses = operations["get"]["responses"]
        assert "422" not in responses, path
        if path != "/api/meta":
            assert responses["400"]["content"]["application/json"]["schema"] == {
                "$ref": "#/components/schemas/ErrorBody"
            }
    assert "HTTPValidationError" not in SCHEMA["components"]["schemas"]
