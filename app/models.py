from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class FreshnessLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class UpdateType(str, Enum):
    price_drop = "price_drop"
    price_rise = "price_rise"
    new_version = "new_version"
    negative_feedback = "negative_feedback"
    positive_feedback = "positive_feedback"
    availability_change = "availability_change"
    other = "other"


class RecommendationItem(BaseModel):
    name: str = Field(min_length=1)
    price_text: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class RecommendationBlock(BaseModel):
    summary: str = Field(min_length=1)
    items: list[RecommendationItem]


class WebUpdate(BaseModel):
    item_name: str = Field(min_length=1)
    update_type: UpdateType
    update_text: str = Field(min_length=1)
    source_title: str = Field(min_length=1)
    source_url: HttpUrl
    published_at: date


class DiffPoint(BaseModel):
    field: str = Field(min_length=1)
    before: str = Field(min_length=1)
    after: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class Freshness(BaseModel):
    level: FreshnessLevel
    score: int = Field(ge=0, le=100)
    label: str = Field(min_length=1)


class AnalyzeResponse(BaseModel):
    query: str = Field(min_length=1, max_length=100)
    base_recommendation: RecommendationBlock
    web_updates: list[WebUpdate]
    revised_recommendation: RecommendationBlock
    diff_points: list[DiffPoint]
    freshness: Freshness
    generated_at: datetime


class ReverseViewResponse(BaseModel):
    item_name: str = Field(min_length=1)
    reverse_text: str = Field(min_length=1)
