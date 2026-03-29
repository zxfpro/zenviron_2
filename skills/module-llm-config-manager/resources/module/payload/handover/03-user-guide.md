# 使用手册

## 本地启动

1. 启动后端

```bash
uv run uvicorn apps.backend.src.main:app --reload --port 8000
```

2. 启动前端

```bash
cd apps/frontend
npm install
npm run dev
```

说明：
- 如 `5173` 被占用，Vite 会自动切到 `5174` 或其他端口，请以终端输出为准。

## 页面操作

### Model Hub

1. 在“已配好的模型”下拉选择方案
2. 修改参数
3. 点击“保存方案”
4. （可选）点击“测试连接”检查连通性

### Model Switch

1. 勾选某方案作为激活方案
2. 点击某行“删除”可删除方案（不可删到最后一个）

## 配置文件位置

- `config/llm_providers.toml`

## 常见问题

- 页面一直 Loading：
  - 检查后端是否启动：`http://127.0.0.1:8000/health`
  - 检查前端真实端口是否变更（看 Vite 终端输出）
- 保存失败：
  - 可能是版本冲突，刷新后重试
