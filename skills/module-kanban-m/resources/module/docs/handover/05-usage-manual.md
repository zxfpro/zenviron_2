# 使用手册

## 1. 启动方式

### 方式 A：本地启动

1. 启动后端
```bash
KANBAN_DATABASE_URL=mysql+pymysql://root:1234@127.0.0.1:3306/kanban_m?charset=utf8mb4 \
uvicorn kanban_api.main:app --app-dir apps/backend/src --host 127.0.0.1 --port 8001
```

2. 启动前端
```bash
cd apps/frontend
VITE_API_BASE=http://127.0.0.1:8001 npm run dev -- --host 127.0.0.1 --port 3000
```

### 方式 B：Docker Compose 启动

```bash
docker compose -f deploy/docker-compose.mysql.yml up -d --build
```

## 2. 访问入口

- 前端：`http://127.0.0.1:3000`
- API 文档：`http://127.0.0.1:8001/docs`
- 健康检查：`http://127.0.0.1:8001/health`

## 3. 业务操作流程

1. 进入看板页查看当前泳道任务
2. 点击“新建任务”创建卡片（默认进预备池）
3. 拖拽卡片跨泳道流转或在泳道内排序
4. 完成任务后可归档
5. 在归档页恢复任务
6. 在团队页查看负载与近期活动
7. 在设置页更新工作区名称与主题

## 4. 常见问题

1. 无法创建任务
- 检查后端是否正常启动
- 检查数据库连接串 `KANBAN_DATABASE_URL`

2. 前端页面空白或接口报错
- 检查 `VITE_API_BASE` 是否指向正确后端地址

3. 拖拽后顺序异常
- 刷新后以服务端状态为准

