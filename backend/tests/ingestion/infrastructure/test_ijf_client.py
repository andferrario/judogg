from collections.abc import Callable

import httpx2
import pytest

from judogg.ingestion.application.errors import CallFailed
from judogg.ingestion.infrastructure.ijf_client import HttpIjfClient

Handler = Callable[[httpx2.Request], httpx2.Response]


class Recorder:
    def __init__(self, *answers: httpx2.Response | Exception) -> None:
        self.answers = list(answers)
        self.requests: list[httpx2.Request] = []
        self.waits: list[float] = []

    def handle(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    def client(self, retries: int = 2, delay_s: float = 1.0) -> HttpIjfClient:
        return HttpIjfClient(
            delay_s=delay_s,
            timeout_s=30,
            retries=retries,
            transport=httpx2.MockTransport(self.handle),
            sleep=self.waits.append,
        )


def test_a_call_encodes_the_brackets_and_names_the_project() -> None:
    recorder = Recorder(httpx2.Response(200, json={"contests": []}))
    payload = recorder.client().get("contest.find", {"id_competition": "3131", "id_weight": "2"})
    assert payload == {"contests": []}
    request = recorder.requests[0]
    assert str(request.url) == (
        "https://data.ijf.org/api/get_json?params%5Baction%5D=contest.find"
        "&params%5Bid_competition%5D=3131&params%5Bid_weight%5D=2"
    )
    assert request.headers["User-Agent"] == "judogg-fetch (personal project)"
    assert recorder.waits == []


def test_empty_json_is_a_valid_answer() -> None:
    assert Recorder(httpx2.Response(200, json=[])).client().get("competition.categories_full", {}) == []


def test_calls_are_spaced_by_the_delay() -> None:
    recorder = Recorder(httpx2.Response(200, json=[]), httpx2.Response(200, json=[]))
    client = recorder.client(delay_s=1.5)
    client.get("a", {})
    client.get("b", {})
    assert recorder.waits == [1.5]


def test_server_errors_are_retried_after_2_then_5_seconds() -> None:
    recorder = Recorder(httpx2.Response(502), httpx2.ConnectError("down"), httpx2.Response(200, json=[1]))
    assert recorder.client().get("a", {}) == [1]
    assert recorder.waits == [2.0, 5.0]


def test_a_call_fails_after_its_retries() -> None:
    recorder = Recorder(httpx2.ReadTimeout("slow"), httpx2.ReadTimeout("slow"), httpx2.Response(503))
    with pytest.raises(CallFailed, match="HTTP 503 after 3 attempts"):
        recorder.client().get("a", {})
    assert len(recorder.requests) == 3


@pytest.mark.parametrize(
    ("answer", "message"),
    [
        (httpx2.Response(404), "HTTP 404"),
        (httpx2.Response(200, content=b"<html>maintenance</html>"), "not JSON"),
        (httpx2.Response(200, content=b"null"), "JSON null"),
    ],
)
def test_answers_that_are_not_retried(answer: httpx2.Response, message: str) -> None:
    recorder = Recorder(answer)
    with pytest.raises(CallFailed, match=message):
        recorder.client().get("a", {})
    assert len(recorder.requests) == 1


def test_html_page_is_a_failed_call() -> None:
    with pytest.raises(CallFailed, match="not JSON"):
        Recorder(httpx2.Response(200, content=b"<html>")).client().get("competition.get_list", {})


@pytest.mark.parametrize("error", [httpx2.DecodingError("broken gzip"), httpx2.TooManyRedirects("loop")])
def test_other_request_errors_are_retried(error: Exception) -> None:
    recorder = Recorder(error, httpx2.Response(200, json=[]))
    assert recorder.client().get("a", {}) == []
    assert recorder.waits == [2.0]
