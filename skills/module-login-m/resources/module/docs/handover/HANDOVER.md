# login_m 交接总览（v1.0）

## 1. 项目目标
`login_m` 是一个可部署的登录模块，支持邮箱与手机两套登录链路，包含前后端页面、后端 API、数据库落盘、测试用例与 Docker 化部署。

## 2. 当前版本状态
- 版本状态：`v1.0`（可交付）
- 后端：FastAPI + SQLModel + JWT
- 前端：静态页面 + Nginx 托管
- 数据库：MySQL（测试服）
- 部署形态：`api + web + mysql` 三容器

## 3. 功能清单（已完成）
- 邮箱注册验证码发送：`POST /auth/register/email/code`
- 邮箱验证码注册：`POST /auth/register_with_code`
- 邮箱密码登录：`POST /auth/login`
- 忘记密码发码：`POST /auth/password/forgot`
- 忘记密码重置：`POST /auth/password/reset`
- 手机验证码发送：`POST /auth/phone/code`
- 手机验证码登录：`POST /auth/phone/login`
- 当前用户查询：`GET /auth/me`
- 健康检查：`GET /health`

## 4. 线上地址（测试服）
- API：`http://115.190.174.181:18000`
- Web：`http://115.190.174.181:18100`
- MySQL：`115.190.174.181:13306`

## 5. 必读文档
- 架构与模块：`docs/handover/ARCHITECTURE.md`
- 使用说明：`docs/handover/USAGE.md`
- 测试用例：`docs/handover/TEST_CASES.md`
- 部署手册：`docs/handover/DEPLOYMENT.md`
- 运维与排障：`docs/handover/OPERATIONS.md`
- 已知问题与改进计划：`docs/handover/ISSUES_AND_PLAN.md`

## 6. 交接结论
当前版本已具备可运行、可测试、可部署、可回归的完整闭环。若进入 `v1.1`，优先项为“手机短信通道从 mock/webhook 升级为火山引擎官方直连”。
