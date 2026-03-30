# Project Structure Overview

本文件定义该前端项目的标准目录结构与职责边界，作为新功能开发时的默认落位规范。

## Directory Tree

```txt
.
├── deploy/
│   └── docker/
│       ├── nginx/
│       │   └── default.conf      # Nginx 配置（含 /health）
│       └── Dockerfile            # 多阶段构建镜像
├── docs/                         # 项目文档
├── public/                       # 原样输出静态资源
├── scripts/                      # 工程脚本（含 init.sh）
├── src/
│   ├── api/
│   │   └── health/               # health API 请求
│   ├── assets/                   # 打包静态资源
│   ├── components/               # 可复用 UI 组件
│   ├── config/                   # 运行配置与环境配置
│   ├── constants/                # 常量定义
│   ├── hooks/
│   │   └── health/               # health 相关 hooks
│   ├── layouts/                  # 布局模板
│   ├── lib/                      # 第三方库二次封装
│   ├── mocks/                    # 本地 mock 数据
│   ├── models/
│   │   └── health/               # health 领域模型
│   ├── pages/                    # 页面级组件
│   ├── router/                   # 路由配置
│   ├── services/                 # 业务服务层
│   ├── store/                    # 全局状态管理
│   ├── styles/                   # 全局样式/主题
│   ├── tests/                    # 测试代码
│   ├── types/
│   │   └── api/                  # API 类型定义
│   ├── utils/                    # 通用工具函数
│   ├── App.tsx
│   ├── main.tsx
│   └── styles.css
├── .dockerignore
├── .env.example
├── docker-compose.yml
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Functional Areas

- 页面层：`src/pages`, `src/layouts`, `src/router`
- 业务层：`src/services`, `src/models`, `src/store`
- 数据通信层：`src/api`, `src/mocks`
- UI 复用层：`src/components`, `src/styles`, `src/assets`
- 基础能力层：`src/utils`, `src/lib`, `src/types`, `src/constants`, `src/config`
- 工程支撑层：`deploy`, `docs`, `scripts`, `public`, `src/tests`

## Placement Rules

- 页面相关代码优先放入 `src/pages`，跨页面复用再下沉到 `src/components`。
- 接口调用统一从 `src/api` 进入，避免在页面中直接发请求。
- 复杂业务编排放在 `src/services`，保持页面组件尽量薄。
- 与业务无关的纯函数放 `src/utils`，与三方库强相关封装放 `src/lib`。
- 类型优先与模块共址；若被多处复用，再提升到 `src/types`。
- 容器部署统一放在 `deploy/docker`，避免与业务代码混放。
