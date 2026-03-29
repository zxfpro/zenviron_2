# Usage

## Quick Start

1. Import payload:
   - `bash "$SKILL_DIR/resources/scripts/import_module.sh" "$SKILL_DIR" "<target-project-dir>"`
2. Start backend:
   - `uv run uvicorn apps.backend.src.main:app --reload --port 8000`
3. Start frontend:
   - `cd apps/frontend && npm install && npm run dev`
4. Open Model Hub / Model Switch and verify behavior.

## Verification

- Test command:
  - `uv run pytest -q`
  - `cd apps/frontend && npm run build`
- E2E command:
  - Manual UI E2E based on `resources/spec/E2E.md`
