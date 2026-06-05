from __future__ import annotations

import logging

from .live_data import LiveProviderError, build_live_response
from .mock_data import build_mock_response
from .models import AnalyzeResponse
from .settings import load_settings

logger = logging.getLogger(__name__)


def analyze_query(query: str) -> AnalyzeResponse:
    settings = load_settings()
    if settings.mode != "live":
        return build_mock_response(query=query)
    try:
        return build_live_response(query=query, settings=settings)
    except LiveProviderError as exc:
        if settings.fallback_to_mock:
            logger.warning("Live mode failed, fallback to mock: %s", exc)
            return build_mock_response(query=query)
        raise