from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_page_served() -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert "推荐校准看板" in resp.text


def test_analyze_contract_stable_keys() -> None:
    resp = client.get("/analyze", params={"query": "相机降价强修正"})
    assert resp.status_code == 200
    data = resp.json()
    assert list(data.keys()) == [
        "query",
        "base_recommendation",
        "web_updates",
        "revised_recommendation",
        "diff_points",
        "freshness",
        "generated_at",
    ]


def test_analyze_empty_lists_are_arrays_not_null() -> None:
    resp = client.get("/analyze", params={"query": "普通查询"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["web_updates"], list)
    assert isinstance(data["diff_points"], list)


def test_analyze_query_length_validation() -> None:
    resp = client.get("/analyze", params={"query": ""})
    assert resp.status_code == 422
    too_long = "a" * 101
    resp2 = client.get("/analyze", params={"query": too_long})
    assert resp2.status_code == 422


def test_three_mock_scenarios() -> None:
    strong = client.get("/analyze", params={"query": "强修正降价"}).json()
    light = client.get("/analyze", params={"query": "轻修正替代"}).json()
    none = client.get("/analyze", params={"query": "常规"}).json()

    assert len(strong["diff_points"]) >= 1
    assert len(light["diff_points"]) >= 1
    assert len(none["diff_points"]) == 0


def test_reverse_view_endpoint_returns_script() -> None:
    resp = client.get("/reverse", params={"item_name": "索尼 ZV-E10"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["item_name"] == "索尼 ZV-E10"
    assert "核心优势" in data["reverse_text"]