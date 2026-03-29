# 功能清单与边界

## 1. 看板页

### 已实现

- 泳道展示（含 `Waiting/等待池`）
- 任务卡片展示（标题、描述、优先级、预估时间、任务编号）
- 新建任务弹窗（标题、描述、优先级、负责人、预估时间）
- 卡片拖拽：
  - 跨泳道移动
  - 泳道内排序
  - 支持中间插入预览
- 卡片操作：归档、删除
- 关键词筛选

### 约束

- 新建任务默认进入 `Backlog`（已移除泳道选择）
- 当前排序仅前端态即时生效，跨泳道后由服务端状态刷新确认

## 2. 归档页

### 已实现

- 查看归档任务列表
- 单任务恢复

## 3. 团队页

### 已实现

- 按泳道任务数量统计工作负载
- 成员任务指标汇总
- 最近活动列表

## 4. 设置页

### 已实现

- 工作区名称读取与更新
- 主题读取与更新（light/dark）

## 5. 后端接口

- `GET /board`
- `GET /tasks`
- `POST /tasks`
- `PATCH /tasks/{id}`
- `DELETE /tasks/{id}`
- `PATCH /tasks/{id}/move`
- `POST /tasks/{id}/archive`
- `POST /tasks/{id}/restore`
- `GET /members`
- `GET /team/metrics`
- `GET /workspace/settings`
- `PATCH /workspace/settings`

