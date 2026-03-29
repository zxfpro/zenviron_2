# Usage

## Quick Start

1. Copy module payload:
   - `cp -R ~/.agents/skills/module-kanban-m/resources/module/* <target-project-dir>/`
2. Backend setup:
   - `cd <target-project-dir>`
   - `uv sync`
3. Frontend setup:
   - `cd <target-project-dir>/apps/frontend`
   - `npm install`
4. Start MySQL + backend + frontend:
   - `docker compose -f deploy/docker-compose.mysql.yml up -d --build`

## Verification

- Test command:
  - `uv run pytest tests/test_api.py`
- E2E command:
  - Run manual core flow from `resources/spec/E2E.md`
