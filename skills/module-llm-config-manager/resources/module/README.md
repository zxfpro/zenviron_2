# Module Payload

This directory contains reusable payload copied from `llm_manager_m`.

## Included

- `payload/apps/backend`: FastAPI config service
- `payload/apps/frontend`: React UI pages and API client
- `payload/config/llm_providers.toml`: default config storage
- `payload/tests`: backend/frontend tests
- `payload/docs/handover`: handover-ready documentation set
- `payload/pyproject.toml`, `payload/README.md`

## Copy Strategy

Use direct copy + integration micro-adjust:

- Keep code structure as-is for fastest adoption.
- Adjust only entry routes, dev/prod proxy, and path conventions.
