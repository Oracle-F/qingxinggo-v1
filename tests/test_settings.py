from __future__ import annotations

from app.settings import load_settings


def test_api_key_is_cleaned_of_whitespace(monkeypatch) -> None:
    monkeypatch.setenv("QXG_API_KEY", "  sk-abc \n 123 \r\n ")
    settings = load_settings()
    assert settings.api_key == "sk-abc123"
