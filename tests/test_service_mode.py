from __future__ import annotations

import pytest

from app import analyze_service
from app.live_data import LiveProviderError
from app.mock_data import build_mock_response


def test_mode_mock_uses_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QXG_MODE", "mock")
    got = analyze_service.analyze_query("常规")
    expected = build_mock_response("常规")
    assert got.query == expected.query
    assert got.base_recommendation.summary == expected.base_recommendation.summary


def test_mode_live_fallback_to_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QXG_MODE", "live")
    monkeypatch.setenv("QXG_FALLBACK_TO_MOCK", "true")
    monkeypatch.setattr(
        analyze_service,
        "build_live_response",
        lambda query, settings: (_ for _ in ()).throw(LiveProviderError("boom")),
    )
    got = analyze_service.analyze_query("常规")
    assert got.query == "常规"


def test_mode_live_no_fallback_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QXG_MODE", "live")
    monkeypatch.setenv("QXG_FALLBACK_TO_MOCK", "false")
    monkeypatch.setattr(
        analyze_service,
        "build_live_response",
        lambda query, settings: (_ for _ in ()).throw(LiveProviderError("boom")),
    )
    with pytest.raises(LiveProviderError):
        analyze_service.analyze_query("常规")
