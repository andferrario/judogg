from app_fakes import THRESHOLDS, EmptyReader
from fastapi.testclient import TestClient

from judogg.app.interfaces.api.dependencies import Services
from judogg.app.interfaces.api.main import create_app

client = TestClient(create_app(lambda: Services(EmptyReader(), THRESHOLDS, ())))


def test_meta_on_an_empty_database() -> None:
    body = client.get("/api/meta").json()
    assert body["defaults"]["ruleset"] == [] and body["defaults"]["year_from"] is None
    assert body["rulesets"] == [] and body["techniques"] == [] and body["coverage"]["excluded"] == []
    assert body["coverage"]["totals"] == {
        "competitions": 0,
        "contests": 0,
        "scores": 0,
        "penalties": 0,
        "athletes": 0,
        "continental_score_share": None,
    }
    assert len(body["weights"]) == 14


def test_filtered_endpoints_on_an_empty_database() -> None:
    for path in (
        "/api/overview",
        "/api/techniques",
        "/api/techniques/by-weight",
        "/api/penalties",
        "/api/outcomes",
        "/api/repertoire/pairs",
    ):
        response = client.get(path)
        assert response.status_code == 200, path
        body = response.json()
        assert body["filters"]["ruleset"] == [] and body["filters"]["year_from"] is None
        assert body["totals"] == {"competitions": 0, "contests": 0, "athletes": 0, "scores": 0, "penalties": 0}
        assert body["warnings"] == []
    overview = client.get("/api/overview").json()["data"]
    assert overview["kpis"]["gs_share"] is None and overview["sample"]["status"] == "insufficient"
    assert client.get("/api/techniques").json()["data"]["rows"] == []


def test_search_on_an_empty_database() -> None:
    assert client.get("/api/athletes", params={"q": "ab"}).json() == {"rows": []}


def test_technique_endpoints_on_an_empty_database_find_no_technique() -> None:
    for path in (
        "/api/techniques/uchi_mata",
        "/api/repertoire?technique=uchi_mata",
        "/api/counters?technique=uchi_mata",
    ):
        assert client.get(path).status_code == 404, path
