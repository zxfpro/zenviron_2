# 改进计划（Roadmap）

## v0.1.3（短期优化）

1. 前端模块化重构
- 将 `App.tsx` 拆分为：
  - `pages/board`、`pages/archive`、`pages/team`、`pages/settings`
  - `components/task-card`、`components/task-create-modal`
  - `hooks/use-board-data`、`hooks/use-drag-sort`

2. 拖拽排序持久化
- 后端新增 `task_order` 字段或独立排序表。
- 新增排序更新 API（批量更新顺序）。

3. 测试完善
- 增加前端单测与关键组件测试（表单、拖拽逻辑）。

## v0.2.0（能力升级）

1. 账号体系与权限
- 登录鉴权（JWT/Session）
- 基于角色的权限控制（RBAC）

2. 高级筛选与搜索
- 多条件过滤（负责人、优先级、泳道、时间范围）
- 服务端分页与排序

3. 活动审计增强
- 记录操作者身份与变更前后值

## v0.3.0（协同体验）

1. 实时协作
- WebSocket 推送卡片变更与活动流

2. 通知系统
- 任务被指派/阻塞/恢复的通知

3. 指标看板升级
- 周期吞吐、在制品数量、阻塞时长等可视化

