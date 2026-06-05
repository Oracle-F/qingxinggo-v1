from __future__ import annotations

import json
import time
from datetime import datetime, timezone

import httpx

from .models import AnalyzeResponse
from .settings import AppSettings


class LiveProviderError(RuntimeError):
    pass


SYSTEM_PROMPT = """你是购物推荐校准助手。请严格输出 JSON，不要输出解释文本。
JSON 必须满足以下结构：
{
  "query": "string",
  "base_recommendation": {"summary": "string", "items": [{"name": "string", "price_text": "string", "reason": "string"}]},
  "web_updates": [{"item_name": "string", "update_type": "price_drop|price_rise|new_version|negative_feedback|positive_feedback|availability_change|other", "update_text": "string", "source_title": "string", "source_url": "https://example.com/x", "published_at": "YYYY-MM-DD"}],
  "revised_recommendation": {"summary": "string", "items": [{"name": "string", "price_text": "string", "reason": "string"}]},
  "diff_points": [{"field": "string", "before": "string", "after": "string", "reason": "string"}],
  "freshness": {"level": "high|medium|low", "score": 0, "label": "string"},
  "generated_at": "ISO-8601 datetime with timezone"
}
要求：
1) 所有字段都必须存在。
2) 无联网更新时 web_updates 返回 []，但 revised_recommendation 仍需返回。
3) 无明显差异时 diff_points 返回 []。
4) query 必须回填用户输入原文。
"""


def _extract_json_text(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
    return text


def _request_chat_completion(query: str, settings: AppSettings) -> str:
    if not settings.api_key:
        raise LiveProviderError("QXG_API_KEY is required when QXG_MODE=live")
    url = settings.api_base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {settings.api_key}"}
    payload = {
        "model": settings.model,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"用户查询：{query}"},
        ],
        "temperature": 0.2,
    }
    data = _request_with_retry(url=url, headers=headers, payload=payload, settings=settings)
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LiveProviderError("Unexpected completion payload shape") from exc


def _is_retryable_status(code: int) -> bool:
    return code == 429 or code >= 500


def _request_with_retry(
    *, url: str, headers: dict[str, str], payload: dict[str, object], settings: AppSettings
) -> dict[str, object]:
    max_attempts = settings.live_max_retries + 1
    last_error: Exception | None = None

    with httpx.Client(timeout=settings.timeout_seconds) as client:
        for attempt in range(1, max_attempts + 1):
            try:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as exc:
                last_error = exc
                status = exc.response.status_code
                if attempt >= max_attempts or not _is_retryable_status(status):
                    if status == 429:
                        raise LiveProviderError(
                            "Live provider rate-limited (429). "
                            "Please retry later, switch to a cheaper model, "
                            "or enable QXG_FALLBACK_TO_MOCK=true."
                        ) from exc
                    raise LiveProviderError(f"Live provider request failed: {exc}") from exc
            except httpx.RequestError as exc:
                last_error = exc
                if attempt >= max_attempts:
                    raise LiveProviderError(f"Live provider request failed: {exc}") from exc

            # Exponential backoff with a tiny cap to keep demo responsiveness.
            delay = min(settings.live_retry_backoff_seconds * (2 ** (attempt - 1)), 6.0)
            if delay > 0:
                time.sleep(delay)

    raise LiveProviderError(f"Live provider request failed: {last_error}")


def build_live_response(query: str, settings: AppSettings) -> AnalyzeResponse:
    raw = _request_chat_completion(query=query, settings=settings)
    json_text = _extract_json_text(raw)
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise LiveProviderError("Model output is not valid JSON") from exc

    data["query"] = query
    data.setdefault("generated_at", datetime.now(timezone.utc).isoformat())
    try:
        return AnalyzeResponse.model_validate(data)
    except Exception as exc:
        raise LiveProviderError("Model output does not match AnalyzeResponse schema") from exc