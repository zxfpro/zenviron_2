# 系统概览

## 目标

`llm_manager_m` 当前阶段目标是提供可视化的大模型方案配置管理能力，并将配置持久化到 TOML 文件，支持页面与文件双向同步。

## 核心能力

- 按 Alias 管理多套模型方案（同 Provider 可多方案）
- Model Hub：编辑方案参数并保存
- Model Switch：切换激活方案、删除方案
- 配置文件持久化：`config/llm_providers.toml`
- 文件监听：外部修改 TOML 后，前端自动感知刷新
- 版本冲突保护：基于 `version_hash`

## 架构图（逻辑）

- 前端（React + Vite）
  - 页面：Model Hub、Model Switch
  - 通过 REST API 读写配置
  - 通过 SSE 监听配置变更
- 后端（FastAPI）
  - 提供配置读写、切换、删除、测试接口
  - 负责 TOML 读写与原子落盘
  - 负责文件监听并广播事件
- 存储
  - TOML 文件：`config/llm_providers.toml`

## 关键数据结构

```toml
[meta]
version = 1
updated_at = "2026-03-25T00:00:00+00:00"
active_alias = "openai_default"

[profiles.openai_default]
provider = "openai"
alias = "openai_default"
...
```

- `meta.active_alias`：当前激活方案
- `profiles.<alias>`：单个方案，`alias` 为唯一标识

## 当前源码入口

- 后端入口：`apps/backend/src/main.py`
- 配置服务：`apps/backend/src/config_service.py`
- 前端入口：`apps/frontend/src/App.tsx`
- Model Hub：`apps/frontend/src/pages/ModelHubPage.tsx`
- Model Switch：`apps/frontend/src/pages/ApiKeysPage.tsx`
