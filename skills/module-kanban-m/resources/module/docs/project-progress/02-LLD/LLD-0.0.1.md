# LLD 0.0.1 - 技术设计

## 技术栈
- 前端：React + Vite + TypeScript + React Router。
- 后端：FastAPI + SQLModel。
- 数据库：MySQL（开发/测试可用 SQLite）。

## 数据模型
- `Workspace`
- `WorkspaceSetting`
- `Member`
- `Column`
- `Task`
- `TaskActivity`

## API 设计
- `GET /board`：返回看板聚合数据（列、任务、成员、工作区名）
- `GET/POST/PATCH/DELETE /tasks`
- `PATCH /tasks/{id}/move`
- `POST /tasks/{id}/archive`
- `POST /tasks/{id}/restore`
- `GET /members`
- `GET /team/metrics`
- `GET/PATCH /workspace/settings`

## 初始化策略
- 启动时自动建表。
- 首次启动自动写入默认工作区、成员、泳道与演示任务。
- 默认泳道顺序：`Backlog -> Ready -> Waiting -> Doing -> Blocked -> Done`。

## 测试设计
- 后端 API 场景测试：
  - 看板聚合初始化
  - 任务 CRUD + 流转 + 归档/恢复
  - 团队指标与设置更新
- 前端交互重点：
  - 新建任务弹窗表单提交
  - 卡片拖拽跨泳道与泳道内排序
  - 归档页与看板页状态联动
