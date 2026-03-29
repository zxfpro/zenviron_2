# 使用说明

## 1. 本地开发
```bash
cd /Users/zxf/GitHub/modules/login_m
uv sync
uv run pytest
uvicorn apps.backend.login_m_backend.main:app --reload
```
前端本地可直接打开：`apps/frontend/index.html`

## 2. 主要 API 调用示例

发送邮箱注册验证码：
```bash
curl -X POST http://localhost:8000/auth/register/email/code \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com"}'
```

邮箱登录：
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"StrongPass123"}'
```

手机发码：
```bash
curl -X POST http://localhost:8000/auth/phone/code \
  -H "Content-Type: application/json" \
  -d '{"phone":"15735182306"}'
```

手机登录：
```bash
curl -X POST http://localhost:8000/auth/phone/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"15735182306","code":"123456"}'
```

## 3. 前端入口
- 登录页内支持：`邮箱登录` 与 `手机登录` 切换
- 注册与忘记密码为邮箱链路
