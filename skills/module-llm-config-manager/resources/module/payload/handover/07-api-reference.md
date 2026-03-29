# API 参考

Base URL（本地）：`http://127.0.0.1:8000`

## 1. 健康检查

- `GET /health`

## 2. 获取配置

- `GET /api/v1/llm-config`

返回：
- `config.meta`
- `config.profiles`
- `version_hash`

## 3. 全量覆盖配置

- `PUT /api/v1/llm-config`

请求体：
- `config`
- `base_version_hash`

## 4. 更新/重命名单方案

- `PATCH /api/v1/llm-config/profiles/{alias}?source_alias={optional}`

请求体：
- `profile`
- `base_version_hash`

说明：
- `source_alias` 不传：更新同名方案
- `source_alias` 传且不等于 path alias：执行重命名语义

## 5. 删除方案

- `DELETE /api/v1/llm-config/profiles/{alias}?base_version_hash=...`

约束：
- 不允许删除最后一个方案

## 6. 设置激活方案

- `POST /api/v1/llm-config/active/{alias}?base_version_hash=...`

## 7. 测试方案连通性

- `POST /api/v1/llm-config/profiles/{alias}/test`

## 8. SSE 变更流

- `GET /api/v1/llm-config/stream`

事件示例：
- `config_replaced`
- `profile_patched`
- `profile_deleted`
- `active_alias_changed`
- `file_changed`
