# Team Quick Start

This page is for teammates who want to review or extend the project without having to read every file first.

## 1. What this project does

- FastAPI service with a stable `GET /analyze?query=...` endpoint
- Mock mode for safe demo runs
- Live mode for OpenAI-compatible `chat/completions`
- Front-end demo page at `/`
- Test suite for core contract and mode switching

## 2. How to run it locally

```powershell
git clone https://github.com/Oracle-F/qingxinggo-v1
cd qingxinggo-v1
.\run.ps1 -Mode mock
```

Then open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## 3. Where to look first

- [README.md](README.md): entry-level run instructions
- [PROJECT_STATUS.md](PROJECT_STATUS.md): current feature map and next-step priorities
- [HANDOFF.md](HANDOFF.md): short transfer note for the next person
- `app/`: backend implementation
- `tests/`: test coverage

## 4. Safe contribution order

1. Read the current flow first.
2. Make a small change.
3. Run tests.
4. Check the front-end page if the UI changed.
5. Keep the mock path stable unless there is a clear reason to touch live mode.

## 5. Good first follow-ups

- Improve the `reverse_view` presentation
- Add confidence scores for `diff_points`
- Add source quality for `web_updates`
- Add a short demo script with fixed queries

## 6. Team rules of thumb

- Keep changes small and stable first.
- Add or update tests with behavior changes.
- Avoid introducing `.env` files or secrets into Git history.
- If you need live mode, set `QXG_API_KEY` locally instead of hardcoding it.
