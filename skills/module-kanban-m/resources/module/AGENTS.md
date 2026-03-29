# Codex 开发指导

## 项目结构(前后端综合项目)

.
├── AGENTS.md // 指导文件
├── CHANGELOG.md // 项目更新日志
├── Dockerfile
├── README.md // 项目概述
├── deploy // 部署相关内容 nginx docker-compose 等文件
│   ├── docker-compose.test.yml
│   ├── docker-compose.prod.yml
│   ├── Readme.md
├── docs
│   ├── connectivity // 相关资源, 外部账户, 账号等 (数据库, 服务器, 大模型)
│   │   ├── Readme.md
│   │   ├── database-config.md
│   │   └── embedding-function.md
│   ├── plans // 开发计划存放位置 
│   └── project-progress // 项目推进过程文档
│       ├── 00-original_demand.md
│       ├── 01-PRD // PRD文档, 版本采用瀑布流模式
│       ├── 02-LLD // LLD文档, 版本采用瀑布流模式 与PRD对齐
│       ├── GANTT.md // 项目进度跟踪与管理-甘特图
│       ├── PROGRESS_DETAILS.md // 项目进度细节记录
│       └── Readme.md
├── .env // 项目环境变量
├── apps
│   ├── frontend // 前端代码
│   │   ├── src //前端源码
│   ├── backend // 后端代码
│   │   ├── src //后端源码
├── node_modules // 前端环境
├── packages
│   ├── shared-types // 前后端共享信息, 结构
├── scripts // 小规模代码功能实验, 运行脚本
│   ├── Readme.md
│   └── notebook // ipynb 文档,笔记本, 人机交互
├── pyproject.toml // python环境管理 uv 配置
├── tests // 测试位置
│   └── static // 测试用例数据
└── uv.lock


## 开发工作流

### 必需步骤
if 初始化
    1 访问docs/project-progress/GANTT.md 了解当前项目进程
    2 阅读docs/project-progress/PROGRESS_DETAILS.md 了解当前进程细节, 阅读当前进行相关的文档,计划, 代码, 进一步掌握细节
3 按照项目指导, 逐步进行开发
4 完成里程碑式的进程后, 在GANTT.md 勾选已完成的任务, 在 PROGRESS_DETAILS.md 中记录当前进度的细节,以便以后快速启动
5 git提交代码, 保存工作进度

项目推进要一步一步来, 并严格按照GANTT.md 中的因果逻辑
所有的评审阶段都必要用户通过, 才能进入下一阶段

## 语言风格
每次和用户沟通的时, 在对话结束后,将下列符号加入到对话的末尾
"😉》^_^《😉"

## api文档
提供一些官方的最新API文档与源码, 位置位于/Users/zxf/api-docs 
当遇到开发过程中API/ Packages 包参数意外错误时, 考虑在此处查询和阅读最新的文档, (不可修改)

## 资源
但有需要与外部联通时, 比如大模型, 服务器, 数据库, 不要光想着自己本地部署, 或者mock , 去docs/connectivity 找找看有没有已经提供的资源

### 先尝试后整合原则
对于一些新的API, 建议先在scripts 文件中编写小规模代码进行验证和实验, 成功后再移植到主项目中, 以减少风险

## 项目交付
1 具备完备的部署文档, 使用文档, 开发文档等文稿, 源码等代码
2 构建一个具备运维和后续升级的专属Agent 配置skills prompt

## Git 工作流
增加代码提交的频率
**提交格式：** `<type>: <description>` — 类型：feat, fix, refactor, docs, test, chore, perf, ci

**PR 工作流：** 分析完整的提交历史 → 起草全面的摘要 → 包含测试计划 → 使用 `-u` 标志推送。

## 版本号管理
- **小修改/debug fix**: `0.1.x` (例如: 0.1.1, 0.1.2)
- **模块调整**: `0.x.0` (例如: 0.2.0)
- **重大调整/重构**: `x.1.0` (例如: 1.0.0)

**版本更新:** 更新包括git 提交, 以及在CHANGELOG.md中 记录更新信息


## 性能

**上下文管理：** 对于大型重构和多文件功能，避免使用上下文窗口的最后 20%。敏感性较低的任务（单次编辑、文档、简单修复）可以容忍较高的利用率。

## 语言

与用户交流使用中文





