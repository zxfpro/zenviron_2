# 部署与运维手册

## 运行前准备

- Python >= 3.10
- Node.js >= 18
- 已安装 `uv`、`npm`

## 本地开发部署

1. 后端

```bash
uv sync
uv run uvicorn apps.backend.src.main:app --host 0.0.0.0 --port 8000
```

2. 前端

```bash
cd apps/frontend
npm install
npm run dev
```

## 生产部署建议

- 后端：`uvicorn + process manager`（systemd/supervisor）
- 前端：`npm run build` 后由 Nginx 托管静态资源
- 反向代理：
  - `/api/*` 转发到后端
  - SSE 端点 `/api/v1/llm-config/stream` 需禁用缓存并保持长连接

## 配置与备份

- 核心配置文件：`config/llm_providers.toml`
- 建议：
  - 每日备份配置文件
  - 变更前自动快照
  - 敏感信息脱敏后再入日志

## 运维排障

1. 后端不通

```bash
curl -sS -i http://127.0.0.1:8000/health
```

2. 前端无法访问
- 检查 Vite 终端输出的实际端口

3. 端口占用

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:5173 -sTCP:LISTEN
```

4. 数据不一致
- 检查是否触发版本冲突（409）
- 检查 TOML 文件是否被外部改写
