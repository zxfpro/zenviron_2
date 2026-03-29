---
name: module-kanban-m
description: Reusable kanban task management module (React + FastAPI + MySQL) with docs/tests/deploy assets.
version: 0.1.0
---

# module-kanban-m

Skill Version: `0.1.0`

Package of the `kanban_m` repository as a reusable module skill.

## When to use

- You want to integrate a ready-to-run Kanban module into another monorepo.
- You need a reference implementation covering board/archive/team/settings pages.
- You need backend APIs, DB model, docs, tests, and Docker Compose deployment baseline.

## Instructions

1. Review module payload under `resources/module/`.
2. Read `resources/spec/INTEGRATION.md` for integration touchpoints.
3. Copy module payload into target project.
4. Configure environment variables and database URL.
5. Run tests and verify core flow.

## Output

- Full-stack module source in `resources/module/`.
- Integration and verification specs in `resources/spec/`.
