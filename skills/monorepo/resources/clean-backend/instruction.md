# Tool Server 项目梳理说明（instruction）

本文档用于系统化梳理 `agent-user-tools` 项目，帮助新成员快速理解该仓库的定位、结构、关键流程与维护重点。

## 1. 项目定位

这是一个基于 FastAPI 的对外 API 服务，核心能力是将 OpenAPI/Swagger 定义的外部接口“工具化”，并提供统一的：

- 工具注册与管理（增删改查、启停）
- 工具分类管理（分组、聚合 schema）
- 工具导入（解析 OpenAPI，预览/测试/批量保存）
- 工具执行（按 schema 发起真实 HTTP 请求）
- 认证鉴权（Redis Token + scope）
- 限流、日志、监控（Prometheus/Grafana/Alertmanager）

一句话：它是一个“API 工具注册与执行中台”。

---

## 2. 技术栈与运行形态

## 2.1 应用层

- Python + FastAPI
- SQLAlchemy ORM（MySQL）
- requests/httpx（外部 HTTP 调用）
- slowapi（速率限制）

## 2.2 基础设施

- MySQL：业务持久化
- Redis：Token 校验、限流存储（可选）
- Nginx：反向代理（HTTP/HTTPS）
- Prometheus：采集指标
- Grafana：监控面板
- Alertmanager：告警分发

## 2.3 主要入口

- 开发入口：`main.py`
- WSGI 入口：`wsgi.py`
- 应用工厂：`app/__init__.py::create_app`

---

## 3. 目录结构（核心）

```txt
app/
  api/          # HTTP 路由层
  services/     # 业务逻辑层
  models/       # ORM 模型
  schemas/      # 请求/响应数据校验模型（Pydantic）
  security/     # Token + scope 鉴权
  utils/        # 响应封装、异常、日志、限流、指标等
  config.py     # 配置加载
  extensions.py # DB 引擎和会话

scripts/
  init_db_mysql.py  # 数据库初始化脚本

docker-compose.yml  # 本地/部署编排（mysql/redis/app/nginx/monitoring）
```

---

## 4. 核心业务对象与存储

## 4.1 业务存储（MySQL）

主要业务模型：

1. `tools`（`app/models/tool.py`）
- 工具名称、描述、图标
- 工具 schema（JSON）
- 状态（enabled/disabled）
- 创建人、创建时间、更新时间

2. `tool_categories`（`app/models/tool_category.py`）
- 分类名称（唯一）、描述、图标
- 状态、排序、创建人、时间

3. `tool_category_associations`（多对多关联表）
- 工具与分类的关联关系

4. `ai_agent`（`app/models/ai_agent.py`）
- 智能体配置相关字段（当前仓库中该模型不是主链路核心）

## 4.2 非业务存储（Redis）

- Token 校验：通过 Redis 中 token 信息验证用户身份与 scope
- 限流后端：可配置 Redis 作为限流存储

---

## 5. 对外 API 设计（v1）

所有主要业务路由挂载在 `/api/v1` 下。

## 5.1 健康检查

- `GET /api/v1/health`

用于容器与网关探活，不依赖数据库。

## 5.2 工具管理（`app/api/tool.py`）

- `GET /api/v1/tools`：分页查询工具
- `GET /api/v1/tools/{tool_id}`：查询单个/多个工具详情
- `POST /api/v1/tools`：创建工具
- `PUT /api/v1/tools/{tool_id}`：更新工具
- `DELETE /api/v1/tools/{tool_id}`：删除工具
- `POST /api/v1/tools/{tool_id}/enable`：启用
- `POST /api/v1/tools/{tool_id}/disable`：停用
- `POST /api/v1/tools/{tool_id}/test`：测试工具
- `POST /api/v1/tools/execute`：执行工具（核心执行入口）

## 5.3 分类管理（`app/api/tool_category.py`）

- `GET /api/v1/categories`：分类列表
- `GET /api/v1/categories/{category_id}`：分类详情 + 工具分页 + 合并 schema
- `POST /api/v1/categories`：创建分类（可选导入 schema 并关联）
- `PUT /api/v1/categories/{category_id}`：更新分类
- `DELETE /api/v1/categories/{category_id}`：删除分类
- `POST /api/v1/categories/{category_id}/enable`：启用分类
- `POST /api/v1/categories/{category_id}/disable`：停用分类

## 5.4 导入能力（`app/api/tool_import.py`）

- `POST /api/v1/tools/preview-schema`：解析 schema 并预览工具，不落库
- `POST /api/v1/tools/test-tool`：保存前测试单工具调用
- `POST /api/v1/tools/batch-save`：批量保存解析后的工具，可归类

---

## 6. 关键调用链路

## 6.1 应用启动链路

1. `main.py` 创建 app
2. `app/__init__.py::create_app`
- 注册 CORS
- 注册限流
- 注册请求日志中间件
- 注册路由
- 注册全局异常处理
- 尝试注册 Prometheus metrics

## 6.2 鉴权链路

1. 路由依赖 `require_scopes([...])`
2. 读取 `Authorization: Bearer <token>`
3. 调用 `RedisTokenService.verify_token`
4. 校验 scopes（支持 `admin` / `*`）
5. 校验失败返回 401/403

## 6.3 工具执行链路（最关键）

入口：`POST /api/v1/tools/execute`

流程：

1. `ToolExecutor.execute(db, tool_id, parameters)`
2. 查询工具并检查工具状态
3. 检查所属分类状态（若有停用分类则拒绝执行）
4. 从工具 schema 提取：
- `server/base_url`
- `path`
- `method`
- `operation`
5. 参数校验（必填参数、重复参数名冲突等）
6. 构建请求 headers / query / body
7. `requests.request(...)` 发起外部调用（支持超时重试）
8. 统一处理并返回响应

## 6.4 OpenAPI 导入链路

1. `preview_schema`：解析 `paths` + HTTP methods
2. `auto_split=true` 时：每个 operation 生成一个工具定义
3. `test_tool`：按 schema 临时发起请求验证可用性
4. `batch_save_tools`：批量入库，必要时创建/关联分类

---

## 7. 配置与环境变量

配置集中在 `app/config.py`，通过 `.env` / 系统环境变量加载。

关键配置分组：

- 应用：`APP_ENV`、`SECRET_KEY`
- 数据库：`DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD`、`DB_NAME`
- Redis：`REDIS_HOST`、`REDIS_PORT`、`REDIS_DB`、`REDIS_PASSWORD`
- 执行：`TOOL_REQUEST_TIMEOUT`、`TOOL_MAX_RETRIES`
- 限流：`RATE_LIMIT_ENABLED`、`RATE_LIMIT_STORAGE_URI`
- 鉴权：`AUTH_ENABLED`、`JWT_SECRET`、`JWT_ALGORITHM`
- 日志：`LOG_LEVEL`、`LOG_DIR` 等

注意：`env.example` 中存在示例密钥/密码，部署前需全部替换。

---

## 8. 部署与运维拓扑

`docker-compose.yml` 启动以下服务：

1. `mysql`：业务数据
2. `redis`：鉴权与限流
3. `app`：FastAPI（Gunicorn + UvicornWorker）
4. `nginx`：反向代理（根据证书自动切换 HTTPS/HTTP-only）
5. `prometheus`：指标采集
6. `alertmanager`：告警管理
7. `grafana`：可视化看板

整体链路：

`Client -> Nginx -> FastAPI App -> MySQL/Redis`

监控链路：

`App metrics -> Prometheus -> Grafana (可视化) + Alertmanager (告警)`

---

## 9. 代码体量与复杂度观察

按当前仓库扫描（仅 Python）：

- `app/ + scripts/` 大约 5.5k 行
- 属于中等规模后端服务

复杂度集中模块：

1. `app/services/tool_category_service.py`
2. `app/services/tool_import_service.py`
3. `app/api/tool_category.py`
4. `app/services/tool_executor.py`

这些文件承载了主要业务规则，改动前建议优先补测试。

---

## 10. 上手与排障建议

## 10.1 新人上手阅读顺序

1. `README.md`
2. `app/__init__.py`
3. `app/api/tool.py`
4. `app/services/tool_executor.py`
5. `app/services/tool_import_service.py`
6. `app/models/*.py`
7. `docker-compose.yml`

## 10.2 最小验证流程

1. 启动 compose
2. `GET /api/v1/health` 确认服务存活
3. 调 `preview-schema` 解析一个 OpenAPI
4. `batch-save` 入库
5. `tools/execute` 执行工具
6. 在 Grafana 查看请求指标变化

## 10.3 常见问题定位

- 401/403：先看 `AUTH_ENABLED` 与 token/scopes
- 执行失败：看 `tool_executor` 参数映射与外部 API 可达性
- 限流异常：检查 `RATE_LIMIT_STORAGE_URI` 与 Redis 连通性
- 数据问题：核对 DB 连接、初始化脚本与表结构

---

## 11. 风险与改进建议（维护视角）

1. 鉴权与环境配置建议强化
- 默认示例密钥不应出现在生产配置
- 建议增加启动时强校验（生产环境禁止默认密钥）

2. 执行引擎稳定性
- 当前按 schema 的“第一个 path+method”提取操作，复杂 schema 可能有歧义
- 建议执行入口明确 operation 标识，减少隐式选择

3. 测试覆盖
- 建议为导入解析、参数构建、重试逻辑、分类启停联动补齐单元/集成测试

4. 观测增强
- 当前已有监控组件，建议补充业务维度指标（按 tool_id、category_id 成功率/耗时分布）

---

## 12. 结论

该项目是一个面向 AI/业务系统的“工具管理与执行中台”：

- 对外提供统一 API
- 有明确数据持久化（MySQL）
- 有鉴权/限流/监控的生产化能力
- 核心价值在“OpenAPI 工具化 + 统一执行编排”

维护时重点关注 `tool_import_service`、`tool_executor` 与鉴权配置安全。
