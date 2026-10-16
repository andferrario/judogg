"""The only module that talks to the IJF."""

import time
from collections.abc import Callable, Mapping
from typing import Any

import httpx2

from judogg.ingestion.application.errors import CallFailed

BASE_URL = "https://data.ijf.org/api/get_json"
RETRY_WAITS_S = (2.0, 5.0)


class HttpIjfClient:
    def __init__(
        self,
        *,
        delay_s: float,
        timeout_s: float,
        retries: int,
        transport: httpx2.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._http = httpx2.Client(timeout=timeout_s, transport=transport)
        self._delay_s = delay_s
        self._retries = retries
        self._sleep = sleep
        self._has_called = False

    def get(self, endpoint: str, params: Mapping[str, str]) -> Any:
        # httpx encodes the brackets: unencoded, they are read as a glob by some clients and the IJF answers nothing
        query = {"params[action]": endpoint} | {f"params[{key}]": value for key, value in params.items()}
        if self._has_called:
            self._sleep(self._delay_s)  # be gentle with the IJF servers
        self._has_called = True
        reason = ""
        for attempt in range(self._retries + 1):
            if attempt:
                self._sleep(RETRY_WAITS_S[min(attempt, len(RETRY_WAITS_S)) - 1])
            try:
                response = self._http.get(BASE_URL, params=query)
            except httpx2.RequestError as error:  # network errors, but also broken bodies and redirect loops
                reason = f"{type(error).__name__} {error}"
                continue
            if response.status_code >= 500:
                reason = f"HTTP {response.status_code}"
                continue
            return _payload(response)
        raise CallFailed(f"{reason} after {self._retries + 1} attempts")

    def close(self) -> None:
        self._http.close()


def _payload(response: httpx2.Response) -> Any:
    if response.status_code != 200:
        raise CallFailed(f"HTTP {response.status_code}")
    try:
        payload = response.json()
    except ValueError as error:
        raise CallFailed("the answer is not JSON") from error
    if payload is None:
        raise CallFailed("the answer is JSON null")  # it would be stored as "not downloaded yet"
    return payload
