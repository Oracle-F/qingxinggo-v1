# 清醒购 V1 交接说明

## 1）当前完成度

- FastAPI 服务可一键运行（`run.ps1` / `run.bat`）。
- `GET /analyze?query=...` 的 V1 接口契约已冻结并可用。
- 内置前端看板可在 `/` 直接演示。
- mock 模式有 3 套固定场景（强修正 / 轻修正 / 无修正）。
- live 模式支持 OpenAI 兼容 `chat/completions`。
- live 异常会返回 `502`，并带可读错误信息。

## 2）最近加固项

- `QXG_API_KEY` 已做清洗（容忍空格/换行，避免粘贴错误）。
- live 请求增加重试与退避，覆盖：
  - `429 Too Many Requests`
  - 临时 `5xx` 与网络请求异常
- live 失败且回退到 mock 时，会在服务日志输出 warning。
- 新增相关测试：重试逻辑、API key 清洗。

## 3）运行方式

```powershell
cd C:\Users\oracl\Documents\Codex\2026-05-08\files-mentioned-by-the-user-docx\qingxinggo_v1
.\run.ps1 -Mode mock
```

live 模式：

```powershell
$env:QXG_MODE="live"
$env:QXG_API_KEY="你的真实key"
$env:QXG_MODEL="gpt-3.5-turbo"
$env:QXG_FALLBACK_TO_MOCK="true"
.\run.ps1 -Mode live
```

接口测试：

```powershell
$u = "http://127.0.0.1:8000/analyze?query=$([uri]::EscapeDataString('我想买一款相机'))"
curl.exe -s $u
```

## 4）已知风险

- live 模式仍受上游限流与网络稳定性影响。
- 输出质量依赖模型遵循提示词能力。
- V1 设计上不含数据库、鉴权、用户历史。

## 5）下一步建议（按优先级）

1. 在响应中新增 `reverse_view`（品牌/商家视角）。
2. 为 `web_updates` 增加来源质量分，为 `diff_points` 增加置信度。
3. 增加短时查询缓存（同 query 短时间复用）。
4. 增加比赛演示脚本（3 条预设请求，一键演示完整流程）。