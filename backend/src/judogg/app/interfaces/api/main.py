from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from judogg.app.interfaces.api.dependencies import Services, build_services
from judogg.app.interfaces.api.errors import install_error_handlers
from judogg.app.interfaces.api.routes import router


def create_app(services_factory: Callable[[], Services] = build_services) -> FastAPI:
    """The services are built at the first request: the OpenAPI schema must be exportable without a database."""
    api = FastAPI(title="Judogg")
    api.state.services_factory = services_factory
    api.state.services = None
    install_error_handlers(api)
    api.include_router(router)
    api.openapi = _openapi_without_422(api)  # type: ignore[method-assign]
    return api


def _openapi_without_422(api: FastAPI) -> Callable[[], dict[str, Any]]:
    """Query parameters are plain strings validated by the application: FastAPI never answers 422."""

    def openapi() -> dict[str, Any]:
        if api.openapi_schema is None:
            schema = get_openapi(title=api.title, version=api.version, routes=api.routes)
            for operations in schema["paths"].values():
                for operation in operations.values():
                    operation["responses"].pop("422", None)
            for name in ("HTTPValidationError", "ValidationError"):
                schema["components"]["schemas"].pop(name, None)
            api.openapi_schema = schema
        return api.openapi_schema

    return openapi


app = create_app()
