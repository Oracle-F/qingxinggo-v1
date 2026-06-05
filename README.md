# 清醒购 V1 API

基于 FastAPI 的最小可演示版本，核心接口为 `GET /analyze`。

## 一键运行

PowerShell：

```powershell
.\run.ps1
```

CMD：

```bat
run.bat
```

`run.ps1` 会自动完成：
- 创建 `.venv` 虚拟环境
- 安装/升级依赖
- 启动 FastAPI（热重载），地址 `http://127.0.0.1:8000`

启动后可访问：
- 前端看板：`http://127.0.0.1:8000/`
- 接口文档：`http://127.0.0.1:8000/docs`

## 手动运行（可选）

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## 接口说明

`GET /analyze?query=...`

- `query`：必填字符串，长度 `1..100`
- 返回固定 `AnalyzeResponse` 结构

## 运行模式

默认模式：`mock`

```powershell
.\run.ps1 -Mode mock
```

实时模式（OpenAI 兼容 `chat/completions`）：

```powershell
$env:QXG_MODE="live"
$env:QXG_API_KEY="your_key"
$env:QXG_API_BASE_URL="https://api.openai.com/v1"
$env:QXG_MODEL="gpt-4.1-mini"
$env:QXG_FALLBACK_TO_MOCK="true"
.\run.ps1 -Mode live
```

说明：
- `QXG_MODE=live` 失败时，若 `QXG_FALLBACK_TO_MOCK=true` 会自动回退 mock。
- mock/live 两种模式下，返回结构完全一致。
- `QXG_API_KEY` 已支持自动清理空格和换行，避免粘贴 key 后请求头报错。
- live 模式内置了 `429`、`5xx`、临时网络错误重试。
- 看板支持“反转视角”，可以把同一商品切换成品牌方话术展示。

可选调参：

```powershell
$env:QXG_LIVE_MAX_RETRIES="2"
$env:QXG_LIVE_RETRY_BACKOFF_SECONDS="1.2"
```

## 测试

```bash
python -m pytest -q
```

## 常见问题

- `Repository not found`：GitHub 仓库地址或 owner 不一致。
- PowerShell 里 `curl` 提示输入 `Uri`：请用 `curl.exe`，不要用 `curl`（它是 `Invoke-WebRequest` 别名）。
- `502 ... 429 Too Many Requests`：上游限流。
  - 等 30-60 秒再试
  - 切换更便宜模型如 `gpt-3.5-turbo`
  - 演示时建议保持 `QXG_FALLBACK_TO_MOCK=true`
- `Could not connect to 127.0.0.1:8000`：服务没在另一个终端窗口持续运行。