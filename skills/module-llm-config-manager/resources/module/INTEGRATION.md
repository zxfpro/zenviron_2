# Integration Guide

## 1) Copy payload

Use script:

```bash
bash "$SKILL_DIR/resources/scripts/import_module.sh" "$SKILL_DIR" "<target-project-dir>"
```

## 2) Backend integration

- Ensure `apps/backend/src/main.py` is runnable via uvicorn.
- Ensure endpoint `/api/v1/llm-config` is reachable.
- Optional env:
  - `LLM_CONFIG_PATH` to customize TOML location.

## 3) Frontend integration

- Ensure routes are mounted:
  - `/hub` -> ModelHubPage
  - `/keys` -> ModelSwitch page
- Ensure proxy forwards `/api/*` to backend service.

## 4) Config sync check

- Edit and save profile in UI, confirm TOML changed.
- Edit TOML manually, confirm UI refreshes via SSE.
