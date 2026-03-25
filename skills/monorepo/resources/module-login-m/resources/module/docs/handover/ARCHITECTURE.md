# 架构说明

## 1. 技术栈
- 后端：FastAPI, SQLModel, PyMySQL, Passlib, PyJWT
- 前端：Vanilla JS + HTML/CSS
- 数据：MySQL 8.4（测试服）
- 部署：Docker Compose（三服务）

## 2. 核心目录
- 后端代码：`apps/backend/login_m_backend/`
- 前端页面：`apps/frontend/`
- 共享类型：`packages/shared-types/auth.ts`
- 测试：`tests/`
- 部署配置：`deploy/docker-compose.test.yml`

## 3. 后端关键模块
- `main.py`：应用入口、路由、鉴权、业务主流程
- `models.py`：`User`、`EmailRegisterCode`、`PasswordResetCode`、`PhoneLoginCode`
- `security.py`：密码哈希与 JWT 编解码
- `email_service.py`：邮件发送器（SMTP/Fake）
- `sms_service.py`：短信发送器（Fake/Webhook）
- `config.py`：环境与资源配置读取

## 4. 登录链路
- 邮箱登录：邮箱+密码 -> JWT
- 手机登录：手机号+验证码 -> JWT（可自动创建手机号用户）

## 5. 数据落盘
- 后端不使用容器内临时存储
- MySQL 数据挂载在卷：`login-m-mysql-data`
- 重建容器后数据保留
