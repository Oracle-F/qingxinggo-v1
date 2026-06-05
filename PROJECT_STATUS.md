# 清醒购 V1 项目现状说明（交接版）

## 1）现在已经实现了哪些功能

1. 一键启动后端服务（自动建虚拟环境、装依赖、启动服务）。
2. 健康检查接口：`GET /health`。
3. 主分析接口：`GET /analyze?query=...`，输入长度限制 `1..100`。
4. 固定响应契约：`AnalyzeResponse` 七大顶层字段稳定输出。
5. mock 三场景输出：
   - 强修正（有价格/口碑变化）
   - 轻修正（新增替代品）
   - 无修正（原推荐有效）
6. live 模式接入大模型（OpenAI 兼容 `chat/completions`）。
7. live 异常处理：
   - 上游异常统一转 `502`
   - 支持回退 mock（`QXG_FALLBACK_TO_MOCK=true`）
   - 支持 `429/5xx/网络异常` 重试与退避
8. 前端演示页面（输入 query、展示基础推荐/修正推荐/更新信息/差异点/新鲜度）。
9. 自动化测试已覆盖核心契约与模式切换，当前通过 `19 passed`。

## 2）这些功能分别由哪些程序实现

- 启动脚本：
  - `run.ps1`（PowerShell）
  - `run.bat`（CMD）

- API 入口与路由：
  - `app/main.py`
  - 负责 `/`、`/health`、`/analyze`

- 接口数据结构（Pydantic）：
  - `app/models.py`
  - 定义 `AnalyzeResponse`、`Freshness`、`DiffPoint`、`WebUpdate` 等

- 业务调度（mock/live 选择与 fallback）：
  - `app/analyze_service.py`

- mock 场景数据：
  - `app/mock_data.py`

- live 调用与解析：
  - `app/live_data.py`
  - 包含模型请求、JSON 抽取、重试机制、错误封装

- 环境变量与运行参数：
  - `app/settings.py`

- 前端页面：
  - `app/static/index.html`
  - `app/static/styles.css`
  - `app/static/app.js`

- 测试：
  - `tests/test_models.py`（模型校验）
  - `tests/test_api.py`（接口契约与返回结构）
  - `tests/test_service_mode.py`（mock/live/fallback 路径）
  - `tests/test_live_data.py`（live JSON 与重试）
  - `tests/test_settings.py`（API key 清洗）

## 3）接下来能做什么（可选增强）

1. 加 `reverse_view`（反转视角）输出块，完善比赛叙事亮点。
2. 给 `web_updates` 增加来源可信度评分。
3. 给 `diff_points` 增加置信度字段，便于前端排序展示。
4. 增加短时缓存，避免同 query 重复打 live 请求。
5. 增加一键演示脚本，固定 3 个 query 快速跑完整流程。

## 4）接下来要做什么（建议优先级）

1. 先保证演示稳定：
   - 默认 `mock` 或 `live + fallback=true`
   - 固定演示 query 和预期结果
2. 再补比赛亮点：
   - 优先实现 `reverse_view`
   - 前端加“原始建议 vs 校准建议”更直观对比区
3. 最后做工程收尾：
   - 完善日志字段（trace id、mode、fallback 标记）
   - 整理提交说明与交接文档

## 5）组员快速上手（3 分钟）

```powershell
cd <repo-root>
.\run.ps1 -Mode mock
```

浏览器打开：
- `http://127.0.0.1:8000/`（看板）
- `http://127.0.0.1:8000/docs`（接口文档）

快速请求：

```powershell
$u = "http://127.0.0.1:8000/analyze?query=$([uri]::EscapeDataString('我想买一款相机'))"
curl.exe -s $u
```
