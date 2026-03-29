# 部署手册（Docker Compose + MySQL）

## 1. 前提条件

- 已安装 Docker 与 Docker Compose
- 可正常访问 Docker Hub（首次拉取镜像需要网络）

## 2. 一键部署

在项目根目录执行：

```bash
docker compose -f deploy/docker-compose.mysql.yml up -d --build
```

## 3. 服务清单

- `mysql`：MySQL 8.4，端口 `3306`
- `backend`：FastAPI 服务，端口 `8001`
- `frontend`：Vite 开发服务，端口 `3000`

## 4. 核心配置

Compose 文件：`deploy/docker-compose.mysql.yml`

后端数据库连接：
`KANBAN_DATABASE_URL=mysql+pymysql://root:1234@mysql:3306/kanban_m?charset=utf8mb4`

前端后端地址：
`VITE_API_BASE=http://127.0.0.1:8001`

## 5. 验证部署

1. 查看容器状态
```bash
docker compose -f deploy/docker-compose.mysql.yml ps
```

2. 健康检查
```bash
curl -sS http://127.0.0.1:8001/health
```

3. 打开页面
- 前端：`http://127.0.0.1:3000`
- API 文档：`http://127.0.0.1:8001/docs`

## 6. 停止与重置

停止：
```bash
docker compose -f deploy/docker-compose.mysql.yml down
```

停止并删除数据卷（重置数据库）：
```bash
docker compose -f deploy/docker-compose.mysql.yml down -v
```

