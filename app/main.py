from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .analyze_service import analyze_query
from .live_data import LiveProviderError
from .models import AnalyzeResponse

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