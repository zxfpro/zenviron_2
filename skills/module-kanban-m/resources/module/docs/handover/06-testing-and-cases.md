# 测试说明与用例

## 1. 测试现状

- 已有后端自动化测试：`tests/test_api.py`
- 冒烟测试：`tests/test_smoke.py`
- 当前覆盖重点：API 行为正确性

## 2. 已有自动化用例（后端）

1. `test_board_bootstrap`
- 校验默认工作区、泳道、成员初始化是否成功

2. `test_task_crud_move_archive_restore`
- 创建任务 -> 更新 -> 移动 -> 归档 -> 恢复 -> 删除

3. `test_metrics_and_settings`
- 校验团队统计接口与设置读写接口

## 3. 建议补充用例

1. 异常路径
- 非法 `column_id` 移动
- 非法 `assignee_id` 指派
- 重复归档/重复恢复

2. 前端交互自动化（E2E）
- 新建任务弹窗提交流程
- 跨泳道拖拽并校验落点
- 泳道内拖拽排序并校验顺序

3. 集成一致性
- 看板页数据与 `/board` 返回一致
- 归档页操作与看板状态联动一致

## 4. 执行命令

```bash
uv run pytest
```

仅跑 API 测试：
```bash
uv run pytest tests/test_api.py
```

