# Integration

## Project touchpoints
- Backend source path target: `apps/backend/login_m_backend/`
- Frontend source path target: `apps/frontend/`
- Deploy files target: `deploy/`

## Minimal wiring
- Ensure reverse proxy `/api` -> backend service.
- Ensure MySQL is reachable from backend container.
- Ensure SMTP env vars are provided for email code.

## Compatibility notes
- Phone SMS currently supports mock or webhook bridge.
- For direct vendor SMS API, extend `sms_service.py`.
