# Integration Guide

## 1. Backend integration
- Mount `backend/login_m_backend` into project backend app.
- Ensure dependencies from `resources/module/pyproject.toml` are installed.
- Start app with `uvicorn ...main:app`.

## 2. Frontend integration
- Serve `frontend/` as static assets.
- Ensure reverse proxy forwards `/api/*` to backend.

## 3. Environment
Required keys:
- `JWT_SECRET`
- `DATABASE_URL`
- SMTP keys for email code
Optional SMS keys:
- `SMS_PROVIDER`
- `SMS_WEBHOOK_ENDPOINT`
- `VOLC_SMS_SIGN_NAME`
- `VOLC_SMS_TEMPLATE_ID`
- `VOLC_SMS_AK`
- `VOLC_SMS_SK`

## 4. Data
- Use MySQL in production.
- Keep DB on persistent volume.
