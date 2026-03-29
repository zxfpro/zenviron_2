# 测试计划与用例

## 测试目标

验证配置管理主链路可用性、稳定性和一致性。

## 已有自动化测试

- 后端：`tests/backend`
  - `test_config_service.py`
  - `test_api.py`
- 前端：基础渲染测试骨架
  - `tests/frontend/modelhub.test.tsx`

## 执行命令

```bash
uv run pytest -q
cd apps/frontend && npm run build
```

## 建议手工回归用例

1. 读取配置
- 打开 Model Hub
- 预期：下拉能看到已配置方案

2. 编辑并保存
- 修改 `model`、`max_tokens`
- 点击保存
- 预期：页面成功提示，TOML 对应字段更新

3. Alias 重命名
- 将 `openai_default` 改为 `openai_main`
- 保存
- 预期：旧 alias 消失，新 alias 存在

4. 切换激活方案
- 到 Model Switch 勾选另一方案
- 预期：`meta.active_alias` 更新

5. 删除方案
- 在 Model Switch 删除一个非唯一方案
- 预期：删除成功；若删的是激活方案，active 自动迁移

6. 文件反向同步
- 手动编辑 TOML
- 预期：页面自动刷新到最新值

## 覆盖缺口（待补）

- 前端交互自动化（RTL/Vitest）
- API 异常场景更细粒度断言（400/404/409）
- SSE 长连接稳定性测试
