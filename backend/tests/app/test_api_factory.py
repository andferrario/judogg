from judogg.app.interfaces.api.dependencies import Services
from judogg.app.interfaces.api.main import create_app


def no_services() -> Services:
    raise AssertionError("the services must not be built with the app")


def test_create_app_builds_the_api_without_a_database() -> None:
    api = create_app(services_factory=no_services)
    assert api.title == "Judogg"
    assert "/api/meta" in api.openapi()["paths"]
