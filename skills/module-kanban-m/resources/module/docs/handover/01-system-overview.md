# 系统概览

## 目标

基于 `code 2.html` 原型，构建可用的看板任务管理系统 MVP，覆盖任务管理、看板流转、归档、团队统计和工作区设置。

## 当前架构

- 前端：React + Vite + TypeScript + React Router
- 后端：FastAPI + SQLModel
- 数据库：MySQL（生产建议），SQLite（开发/测试可选）
- 启动方式：本地进程启动 / Docker Compose 启动

## 目录结构（核心）

- `apps/frontend/src/App.tsx`：当前前端主要页面与交互逻辑
- `apps/backend/src/kanban_api/api.py`：核心 API 路由
- `apps/backend/src/kanban_api/models.py`：数据模型
- `apps/backend/src/kanban_api/seed.py`：初始化数据
- `deploy/docker-compose.mysql.yml`：MySQL 一体化部署编排

## 核心数据模型

- `Workspace`：工作区
- `WorkspaceSetting`：工作区配置（名称、主题）
- `Member`：成员与角色标签
- `Column`：泳道定义
- `Task`：任务实体
- `TaskActivity`：任务活动记录

## 默认泳道

`Backlog -> Ready -> Waiting -> Doing -> Blocked -> Done`

## 非目标（v0.1.x）

- 不实现登录鉴权
- 不实现权限拦截（角色仅用于展示/指派/统计）
- 不实现复杂实时协同（WebSocket）

