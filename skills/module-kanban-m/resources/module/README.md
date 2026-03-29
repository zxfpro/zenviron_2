# kanban_m

看板任务管理系统（v0.1.x），基于 `React(Vite) + FastAPI + MySQL`。

## Quick Start

1) 安装 Python 依赖
```bash
uv sync
```

2) 启动后端（默认读取 `KANBAN_DATABASE_URL`，未配置时使用本地 MySQL）
```bash
uvicorn kanban_api.main:app --app-dir apps/backend/src --reload
```

3) 启动前端
```bash
cd apps/frontend
npm run dev
```

4) 运行测试
```bash
uv run pytest
```

## API 概览

- `GET /board`
- `GET/POST/PATCH/DELETE /tasks`
- `PATCH /tasks/{id}/move`
- `POST /tasks/{id}/archive`
- `POST /tasks/{id}/restore`
- `GET /members`
- `GET /team/metrics`
- `GET/PATCH /workspace/settings`

## Structure

- `apps/frontend` - Next.js 前端
- `apps/backend/src/kanban_api` - FastAPI 后端
- `packages/shared-types` - 共享类型草案
- `docs/project-progress` - PRD/LLD/进度文档
- `tests` - 测试用例

## Docker Compose（MySQL 一键启动）

项目已提供 `deploy/docker-compose.mysql.yml`，包含 `mysql + backend + frontend`。

1) 启动
```bash
docker compose -f deploy/docker-compose.mysql.yml up -d --build
```

2) 访问
- 前端: `http://127.0.0.1:3000`
- 后端: `http://127.0.0.1:8001`
- OpenAPI: `http://127.0.0.1:8001/docs`

3) 停止
```bash
docker compose -f deploy/docker-compose.mysql.yml down
```

4) 停止并清空数据库卷
```bash
docker compose -f deploy/docker-compose.mysql.yml down -v
```
