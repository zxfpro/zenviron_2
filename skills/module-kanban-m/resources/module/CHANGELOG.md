# 更新日志

## 0.1.3 - 2026-03-26

### docs
- 新增交接文档包：`docs/handover/*`，覆盖系统概览、功能清单、已知问题、改进计划、使用手册、测试说明、部署手册、运维 Runbook。
- 更新 `docs/Readme.md` 为文档索引。
- 修正 `PRD-0.0.1`、`LLD-0.0.1` 与当前实现不一致内容（前端栈、泳道、交互能力）。
- 更新 `GANTT.md` 与 `PROGRESS_DETAILS.md` 的交付文档进度状态。

## 0.1.2 - 2026-03-26

### feat
- 新增 `deploy/docker-compose.mysql.yml`，支持通过 Docker Compose 一键启动 `MySQL + FastAPI + React(Vite)`。
- 新增 `apps/backend/Dockerfile` 与 `apps/frontend/Dockerfile`，用于容器化运行后端与前端服务。

### docs
- 更新 `README.md`：补充 Docker Compose 启动、访问、停止、清理卷说明。

## 0.1.1 - 2026-03-25

### feat
- 新增 FastAPI 后端与 SQLModel 数据模型，覆盖任务、泳道、成员、活动、工作区设置。
- 新增 API：`/board`、`/tasks`、`/tasks/{id}/move`、`/tasks/{id}/archive|restore`、`/members`、`/team/metrics`、`/workspace/settings`。
- 新增系统初始化逻辑：启动自动建表并注入默认工作区/成员/泳道/演示任务。
- 新增 Next.js 前端四页面：看板、归档、团队、设置，并接入真实后端 API。

### test
- 新增 `tests/test_api.py`，覆盖核心业务流程（CRUD、流转、归档/恢复、设置）。

### docs
- 补充 PRD/LLD 文档，更新 GANTT 与项目进程细节文档。
