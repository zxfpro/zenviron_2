---
name: project-backend-dev
description: Implement and evolve backend features for this FastAPI project, including API routes, schemas, services, persistence, and auth-aware integrations. Use when adding new backend functionality, wiring incomplete template modules, fixing backend runtime errors, or extending domain logic under app/api, app/models, app/schemas, app/services, app/security, and app/extensions.
---

# Project Backend Dev

## Workflow

1. Read current module boundaries before coding.
2. Implement minimal vertical slices from route to storage.
3. Keep interfaces explicit between `schemas`, `services`, and `models`.
4. Add tests for each new behavior before merging.
5. Run local checks and confirm startup path stays healthy.

## Implementation Rules

- Prefer small, composable service functions over large endpoint handlers.
- Keep route layer thin: validate input, call service, map response.
- Keep persistence logic in service/model layer, not route handlers.
- Reuse `app.config.settings` and avoid hardcoded env values.
- Preserve backward compatibility for existing response fields unless user asks to break.

## FastAPI Slice Pattern

1. Define request/response models in `app/schemas`.
2. Define ORM/SQLModel entities in `app/models`.
3. Implement business logic in `app/services`.
4. Register router in `app/__init__.py` via `register_routers`.
5. Add smoke tests for endpoint status and key payload fields.

## Startup Safety

- Guard optional integrations with config toggles.
- Avoid importing unfinished modules at import time; defer when needed.
- Keep `create_app()` and lifespan deterministic.

## References

- Read `references/checklists.md` before implementing larger features.
