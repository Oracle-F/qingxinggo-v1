from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models import (
    AnalyzeResponse,
    DiffPoint,
    Freshness,
    FreshnessLevel,
    RecommendationBlock,
    RecommendationItem,
)


def _valid_payload() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "query": "我想买一款相机",
        "base_recommendation": {
            "summary": "基础推荐",
            "items": [
                {"name": "A", "price_text": "100元", "reason": "理由"},
            ],
        },
        "web_updates": [
            {
                "item_name": "A",
                "update_type": "price_drop",
                "update_text": "降价",
                "source_title": "来源",
                "source_url": "https://example.com",
                "published_at": "2026-04-29",
            }
        ],
        "revised_recommendation": {
            "summary": "修正推荐",
            "items": [
                {"name": "A", "price_text": "99元", "reason": "修正理由"},
            ],
        },
        "diff_points": [
            {"field": "price", "before": "100元", "after": "99元", "reason": "降价"}
        ],
        "freshness": {"level": "medium", "score": 68, "label": "存在更新"},
        "generated_at": now,
    }


def test_valid_model_payload_passes() -> None:
    payload = _valid_payload()
    model = AnalyzeResponse.model_validate(payload)
    assert model.query == payload["query"]
    assert model.freshness.level == FreshnessLevel.medium


@pytest.mark.parametrize("score", [-1, 101])
def test_invalid_score_fails(score: int) -> None:
    payload = _valid_payload()
    payload["freshness"]["score"] = score
    with pytest.raises(ValidationError):
        AnalyzeResponse.model_validate(payload)


def test_invalid_level_fails() -> None:
    payload = _valid_payload()
    payload["freshness"]["level"] = "urgent"
    with pytest.raises(ValidationError):
        AnalyzeResponse.model_validate(payload)


def test_invalid_date_format_fails() -> None:
    payload = _valid_payload()
    payload["web_updates"][0]["published_at"] = "2026/04/29"
    with pytest.raises(ValidationError):
        AnalyzeResponse.model_validate(payload)


def test_diff_point_requires_before_after_reason() -> None:
    with pytest.raises(ValidationError):
        DiffPoint.model_validate({"field": "price", "before": "100"})


def test_query_length_constraints() -> None:
    base = RecommendationBlock(
        summary="ok",
        items=[RecommendationItem(name="A", price_text="1", reason="r")],
    )
    with pytest.raises(ValidationError):
        AnalyzeResponse(
            query="",
            base_recommendation=base,
            web_updates=[],
            revised_recommendation=base,
            diff_points=[],
            freshness=Freshness(level=FreshnessLevel.high, score=99, label="ok"),
            generated_at=datetime.now(timezone.utc),
        )