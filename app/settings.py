from __future__ import annotations

import os
from dataclasses import dataclass


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppSettings:
    mode: str
    api_base_url: str
    api_key: str | None
    model: str
    timeout_seconds: float
    fallback_to_mock: bool
    live_max_retries: int
    live_retry_backoff_seconds: float


def _clean_api_key(value: str | None) -> str | None:
    if value is None:
        return None
    # Be tolerant to accidental line wraps/pasted whitespace in terminal.
    cleaned = "".join(value.split())
    return cleaned or None


def load_settings() -> AppSettings:
    return AppSettings(
        mode=os.getenv("QXG_MODE", "mock").strip().lower(),
        api_base_url=os.getenv("QXG_API_BASE_URL", "https://api.openai.com/v1").strip(),
        api_key=_clean_api_key(os.getenv("QXG_API_KEY")),
        model=os.getenv("QXG_MODEL", "gpt-4.1-mini").strip(),
        timeout_seconds=float(os.getenv("QXG_TIMEOUT_SECONDS", "45")),
        fallback_to_mock=_as_bool(os.getenv("QXG_FALLBACK_TO_MOCK"), default=True),
        live_max_retries=max(int(os.getenv("QXG_LIVE_MAX_RETRIES", "2")), 0),
        live_retry_backoff_seconds=max(
            float(os.getenv("QXG_LIVE_RETRY_BACKOFF_SECONDS", "1.2")), 0.0
        ),
    )