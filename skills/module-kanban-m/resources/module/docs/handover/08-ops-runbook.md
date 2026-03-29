# 运维 Runbook

## 1. 常用运维命令

查看服务状态：
```bash
docker compose -f deploy/docker-compose.mysql.yml ps
```

查看后端日志：
```bash
docker compose -f deploy/docker-compose.mysql.yml logs -f backend
```

查看前端日志：
```bash
docker compose -f deploy/docker-compose.mysql.yml logs -f frontend
```

查看数据库日志：
```bash
docker compose -f deploy/docker-compose.mysql.yml logs -f mysql
```

## 2. 故障排查

1. 后端无法启动
- 检查 `KANBAN_DATABASE_URL`
- 检查 MySQL 是否健康（`docker compose ps`）

2. 前端请求失败（CORS/连接拒绝）
- 检查前端环境变量 `VITE_API_BASE`
- 检查后端 `8001` 端口监听

3. 数据异常
- 先导出数据，再决定是否 `down -v` 重置

## 3. 数据库连通性检查

```bash
docker compose -f deploy/docker-compose.mysql.yml exec mysql \
  mysql -uroot -p1234 -e "SHOW DATABASES; USE kanban_m; SHOW TABLES;"
```

## 4. 日常巡检建议

1. 每日检查 `/health`
2. 关注后端错误日志（5xx / SQL 异常）
3. 每次升级前执行自动化测试：`uv run pytest`
4. 每次发布后验证关键链路：
- 看板加载
- 新建任务
- 拖拽移动
- 归档恢复

