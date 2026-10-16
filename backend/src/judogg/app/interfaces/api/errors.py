from typing import cast

from fastapi import FastAPI, Request, Response
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from judogg.app.application.errors import InvalidParameter, NotFound


def _error(status: int, code: str, message: str, field: str | None) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message, "field": field}})


async def _invalid_parameter(_: Request, error: Exception) -> Response:
    problem = cast(InvalidParameter, error)
    return _error(400, "invalid_parameter", problem.message, problem.field)


async def _not_found(_: Request, error: Exception) -> Response:
    problem = cast(NotFound, error)
    return _error(404, "not_found", problem.message, problem.field)


async def _validation(_: Request, error: Exception) -> Response:
    first = cast(RequestValidationError, error).errors()[0]
    return _error(400, "invalid_parameter", str(first["msg"]), str(first["loc"][-1]))


async def _http(request: Request, error: Exception) -> Response:
    problem = cast(HTTPException, error)
    if problem.status_code == 404:
        return _error(404, "not_found", f"unknown endpoint {request.url.path}", None)
    return await http_exception_handler(request, problem)


def install_error_handlers(api: FastAPI) -> None:
    api.add_exception_handler(InvalidParameter, _invalid_parameter)
    api.add_exception_handler(NotFound, _not_found)
    api.add_exception_handler(RequestValidationError, _validation)
    api.add_exception_handler(HTTPException, _http)
