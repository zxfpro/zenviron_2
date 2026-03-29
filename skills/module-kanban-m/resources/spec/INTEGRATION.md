# Integration Guide

Use direct copy + micro-adjust strategy.

## Touchpoints

- Route mounting:
  - Frontend routes are in `apps/frontend/src/App.tsx` (`/`, `/archive`, `/team`, `/settings`).
- Config/env wiring:
  - Backend: `KANBAN_DATABASE_URL`
  - Frontend: `VITE_API_BASE`
- DB migration entry:
  - Current module uses SQLModel auto-create in startup (`create_db_and_tables()`), no Alembic yet.
- App bootstrap registration:
  - Backend entry: `kanban_api.main:app`
  - Frontend entry: Vite + React app under `apps/frontend`.

## Rules

- Keep original project style and structure.
- Only modify integration boundaries.
- Do not refactor unrelated business code.
