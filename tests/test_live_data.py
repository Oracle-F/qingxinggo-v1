from __future__ import annotations

import json
from datetime import datetime

import httpx
import pytest

from app.live_data import _extract_json_text, _request_with_retry, build_live_response
from app.settings import AppSettings


def test_extract_json_text_from_fenced_block() -> None:
    wrapped = "```json\n{\"a\":1}\n```"
    assert _extract_json_text(wrapped) == "{\"a\":1}"


def test_build_live_response_parses_valid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = AppSettings(
        mode="live",
        api_base_url="https://example.com/v1",
        api_key="dummy",
        model="dummy-model",
        timeout_seconds=10,
        fallback_to_mock=True,
        live_max_retries=2,
        live_retry_backoff_seconds=0.1,
    )
    payload = {
        "query": "会被覆盖",
        "base_recommendation": {
            "summary": "base",
            "items": [{"name": "A", "price_text": "100", "reason": "r"}],
        },
        "web_updates": [],
        "revised_recommendation": {
            "summary": "rev",
            "items": [{"name": "A", "price_text": "99", "reason": "r2"}],
        },
        "diff_points": [],
        "freshness": {"level": "high", "score": 90, "label": "ok"},
        "generated_at": datetime.now().astimezone().isoformat(),
    }

    monkeypatch.setattr(
        "app.live_data._request_chat_completion",
        lambda query, settings: json.dumps(payload),
    )
    result = build_live_response(query="真实查询", settings=settings)
    assert result.query == "真实查询"
    assert result.base_recommendation.items[0].name == "A"


def test_request_with_retry_recovers_after_429(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = AppSettings(
        mode="live",
        api_base_url="https://example.com/v1",
        api_key="dummy",
        model="dummy-model",
        timeout_seconds=10,
        fallback_to_mock=True,
        live_max_retries=2,
        live_retry_backoff_seconds=0.1,
    )
    calls = {"n": 0}

    class _FakeClient:
        def __init__(self, timeout: float) -> None:
            self.timeout = timeout

        def __enter__(self) -> "_FakeClient":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def post(self, url: str, headers: dict[str, str], json: dict[str, object]):
            calls["n"] += 1
            if calls["n"] == 1:
                request = httpx.Request("POST", url)
                response = httpx.Response(429, request=request)
                raise httpx.HTTPStatusError("rate limited", request=request, response=response)
            return _OkResponse()

    class _OkResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"ok": True}

    monkeypatch.setattr("app.live_data.httpx.Client", _FakeClient)
    monkeypatch.setattr("app.live_data.time.sleep", lambda _: None)
    result = _request_with_retry(
        url="https://example.com/v1/chat/completions",
        headers={"Authorization": "Bearer x"},
        payload={"model": "x"},
        settings=settings,
    )
    assert result["ok"] is True
    assert calls["n"] == 2