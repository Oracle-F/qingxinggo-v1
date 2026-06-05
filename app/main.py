from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .analyze_service import analyze_query
from .live_data import LiveProviderError
from .models import AnalyzeResponse, ReverseViewResponse

app = FastAPI(title="QingXingGo V1 API", version="0.1.0")
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/analyze", response_model=AnalyzeResponse)
def analyze(
    query: str = Query(..., min_length=1, max_length=100, description="User query text")
) -> AnalyzeResponse:
    try:
        return analyze_query(query=query)
    except LiveProviderError as exc:
        # Return actionable upstream error instead of opaque 500.
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/reverse", response_model=ReverseViewResponse)
def reverse_view(item_name: str = Query(..., min_length=1, max_length=100)) -> ReverseViewResponse:
    scripts: dict[str, str] = {
        "索尼 ZV-E10": (
            "索尼 ZV-E10 专为 Vlog 创作者设计，轻量化机身是它的核心优势。"
            "我们没有增加防水密封结构，是为了让机身更轻盈、散热更高效。"
            "这对于长时间录制视频的用户来说，远比偶尔遇到的潮湿环境更重要。"
        ),
        "佳能 EOS R50": (
            "佳能 EOS R50 的定位是入门级用户的第一台相机。我们深知这个群体最在意的是"
            "易用性和性价比，因此在机身防抖和耐候性上做了取舍。"
            "这不是缺陷，而是为了让更多年轻人以更低门槛进入摄影世界。"
        ),
        "尼康 Z30": (
            "尼康 Z30 专注于视频创作者。我们没有采用高端机型的全密封设计，"
            "因为视频用户更看重轻便和散热表现。每一款产品都有它的目标用户。"
        ),
    }
    default = (
        f"{item_name} 的每一项设计都经过了反复权衡。我们选择在某些方面做减法，"
        "是为了在其他方面做加法，让产品更聚焦于目标用户的核心需求。"
    )
    for key, script in scripts.items():
        if key in item_name or item_name in key:
            return ReverseViewResponse(item_name=item_name, reverse_text=script)
    return ReverseViewResponse(item_name=item_name, reverse_text=default)
