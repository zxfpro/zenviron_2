---
name: module-llm-config-manager
description: Reusable LLM multi-profile config manager (React + FastAPI + TOML sync).
version: 0.2.0
---

# module-llm-config-manager

Skill Version: `0.2.0`

This skill packages a production-ready module for managing third-party LLM profiles
with alias-based switching, TOML persistence, and page-file bidirectional sync.

## When to use

- You need a reusable LLM provider/profile management module.
- You want alias-based model profile switching and deletion out of the box.
- You want a direct-copy payload with integration micro-adjust guidance.

## Instructions

1. Import payload into target project:
   - `bash "$SKILL_DIR/resources/scripts/import_module.sh" "$SKILL_DIR" "<target-project-dir>"`
2. Follow integration steps in:
   - `resources/module/INTEGRATION.md`
3. Follow usage and verification in:
   - `resources/spec/USAGE.md`
4. Run local checks:
   - `uv run pytest -q`
   - `cd apps/frontend && npm run build`

## Output

- Frontend pages: `Model Hub`, `Model Switch`
- Backend API: profile CRUD + active alias + SSE sync
- Config file: `config/llm_providers.toml`
- Handover docs: `docs/handover/*`
