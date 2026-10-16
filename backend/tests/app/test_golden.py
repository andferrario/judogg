import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from golden_compare import assert_same

from judogg.app.interfaces.api.main import create_app

GOLDEN = Path(__file__).parents[1] / "fixtures" / "api"
# Every directory is a group: a new one cannot be skipped by forgetting to list it.
GROUPS = sorted(d.name for d in GOLDEN.iterdir() if d.is_dir())
CASES = sorted(case for group in GROUPS for case in (GOLDEN / group).glob("*.json"))


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


@pytest.mark.parametrize("case", CASES, ids=lambda case: f"{case.parent.name}/{case.stem}")
def test_response_matches_the_golden_one(client: TestClient, case: Path) -> None:
    golden: dict[str, Any] = json.loads(case.read_text(encoding="utf-8"))
    response = client.get(golden["path"], params=golden["query"])
    assert response.status_code == golden["status"], response.text
    assert_same(response.json(), golden["body"])


def test_unknown_query_parameters_are_ignored(client: TestClient) -> None:
    assert client.get("/api/meta", params={"foo": "1", "gender": "x"}).status_code == 200


def test_page_beyond_the_last_is_empty(client: TestClient) -> None:
    body = client.get("/api/techniques/uchi_mata/scores", params={"page": "999"}).json()
    assert body["data"]["rows"] == [] and body["data"]["total"] > 0


def test_a_shido_reason_is_not_a_technique(client: TestClient) -> None:
    response = client.get("/api/techniques/non_combativity")
    assert response.status_code == 404 and response.json()["error"]["field"] == "technique"


@pytest.mark.parametrize("athlete_id", ["abc", "99999999999999999999", "-1"])
def test_malformed_athlete_ids_are_not_found(client: TestClient, athlete_id: str) -> None:
    response = client.get(f"/api/athletes/{athlete_id}")
    assert response.status_code == 404 and response.json()["error"]["field"] == "athlete"
