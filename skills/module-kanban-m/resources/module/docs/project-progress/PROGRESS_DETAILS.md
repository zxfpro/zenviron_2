# 进程细节

## 2026-03-25

### 已完成
- 落地前后端 MVP 全链路：
  - 前端 `Next.js` 四页面：看板、归档、团队、设置
  - 后端 `FastAPI` 任务域 API 与聚合接口
- 完成数据模型与初始化策略：
  - `Workspace/WorkspaceSetting/Member/Column/Task/TaskActivity`
  - 启动自动建表与默认数据写入
- 完成后端测试：
  - 看板初始化
  - 任务 CRUD + 流转 + 归档恢复
  - 团队指标与设置更新
- 补齐 PRD/LLD 文档并更新 GANTT 勾选。

### 当前版本状态
- 版本基线：`0.1.0`
- 状态：具备可运行 MVP，待进入体验走查与需求修正阶段

## 2026-03-26

### 已完成
- 接入 MySQL 容器化部署能力：
  - 新增 `deploy/docker-compose.mysql.yml`（mysql + backend + frontend）
  - 新增 `apps/backend/Dockerfile`、`apps/frontend/Dockerfile`
  - 新增 `.dockerignore` 降低构建上下文体积
- 完成交接文档包：
  - 系统概览、功能清单、已知问题、改进计划
  - 使用手册、测试说明、部署手册、运维 Runbook
- 修正文档与实现不一致问题：
  - PRD/LLD 中前端技术栈修正为 `React + Vite`

### 待完成
- 在目标环境执行完整部署演练并记录结果
- 补齐前端自动化测试与 E2E 测试
- 推进测试阶段（功能/集成/压力/回归）

### 当前版本状态
- 当前开发版本：`0.1.2`
- 状态：功能可用，具备交接基础文档，待完成部署实测与测试体系增强
