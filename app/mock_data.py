from __future__ import annotations

from datetime import date, datetime, timezone

from .models import (
    AnalyzeResponse,
    DiffPoint,
    Freshness,
    FreshnessLevel,
    RecommendationBlock,
    RecommendationItem,
    UpdateType,
    WebUpdate,
)


def _mock_strong(query: str) -> AnalyzeResponse:
    return AnalyzeResponse(
        query=query,
        base_recommendation=RecommendationBlock(
            summary="基于模型知识的基础推荐结论",
            items=[
                RecommendationItem(
                    name="索尼 ZV-E10",
                    price_text="约4500元",
                    reason="口碑优秀，适合入门视频创作",
                )
            ],
        ),
        web_updates=[
            WebUpdate(
                item_name="索尼 ZV-E10",
                update_type=UpdateType.price_drop,
                update_text="官方降价至3999元，二代已发布",
                source_title="品牌官方公告",
                source_url="https://example.com/sony-zve10-update",
                published_at=date(2026, 4, 29),
            ),
            WebUpdate(
                item_name="索尼 ZV-E10",
                update_type=UpdateType.negative_feedback,
                update_text="近一个月出现新增防水相关使用投诉",
                source_title="用户反馈汇总",
                source_url="https://example.com/sony-feedback",
                published_at=date(2026, 4, 30),
            ),
        ],
        revised_recommendation=RecommendationBlock(
            summary="结合联网信息后的修正建议",
            items=[
                RecommendationItem(
                    name="佳能 EOS R50",
                    price_text="约4300元",
                    reason="近期口碑稳定，入门性价比更均衡",
                )
            ],
        ),
        diff_points=[
            DiffPoint(
                field="price",
                before="约4500元",
                after="3999元",
                reason="发现官方最新降价信息",
            ),
            DiffPoint(
                field="risk",
                before="口碑优秀",
                after="需关注近期新增投诉",
                reason="联网发现新增负面反馈",
            ),
        ],
        freshness=Freshness(
            level=FreshnessLevel.medium, score=68, label="存在部分信息更新"
        ),
        generated_at=datetime.now(timezone.utc),
    )


def _mock_light(query: str) -> AnalyzeResponse:
    return AnalyzeResponse(
        query=query,
        base_recommendation=RecommendationBlock(
            summary="基于模型知识的基础推荐结论",
            items=[
                RecommendationItem(
                    name="索尼 ZV-E10",
                    price_text="约4500元",
                    reason="视频表现稳定",
                )
            ],
        ),
        web_updates=[
            WebUpdate(
                item_name="佳能 EOS R50",
                update_type=UpdateType.positive_feedback,
                update_text="近期新增入门用户正向评价",
                source_title="测评社区周报",
                source_url="https://example.com/r50-positive",
                published_at=date(2026, 4, 18),
            )
        ],
        revised_recommendation=RecommendationBlock(
            summary="基础推荐保持不变，补充可比较候选",
            items=[
                RecommendationItem(
                    name="索尼 ZV-E10",
                    price_text="约4500元",
                    reason="核心表现稳定",
                ),
                RecommendationItem(
                    name="佳能 EOS R50",
                    price_text="约4300元",
                    reason="新增替代候选，近期评价稳定",
                ),
            ],
        ),
        diff_points=[
            DiffPoint(
                field="alternatives",
                before="未提供",
                after="新增佳能 EOS R50",
                reason="联网发现近期可比候选",
            )
        ],
        freshness=Freshness(level=FreshnessLevel.high, score=86, label="信息较新"),
        generated_at=datetime.now(timezone.utc),
    )


def _mock_none(query: str) -> AnalyzeResponse:
    block = RecommendationBlock(
        summary="联网未发现明显新增变动，基础推荐保持有效",
        items=[
            RecommendationItem(
                name="索尼 ZV-E10",
                price_text="约4500元",
                reason="当前可见信息与基础结论一致",
            )
        ],
    )
    return AnalyzeResponse(
        query=query,
        base_recommendation=block,
        web_updates=[],
        revised_recommendation=block,
        diff_points=[],
        freshness=Freshness(level=FreshnessLevel.high, score=92, label="暂未发现新变动"),
        generated_at=datetime.now(timezone.utc),
    )


def build_mock_response(query: str) -> AnalyzeResponse:
    """Return one of three fixed mock scenarios for deterministic contract testing."""
    q = query.lower()
    if "强" in query or "price" in q or "降价" in query:
        return _mock_strong(query)
    if "轻" in query or "替代" in query:
        return _mock_light(query)
    return _mock_none(query)