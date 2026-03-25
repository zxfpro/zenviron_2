---
name: module-login-m
description: Reusable login module with email + phone auth, MySQL persistence, Docker deployment, and handover docs.
version: 1.0.0
---

# module-login-m

Skill Version: `1.0.0`

Reusable full-stack login module extracted from `login_m`.
Supports direct copy + integration micro-adjust for monorepo projects.

## When to use

- You need a ready-to-integrate auth module (email register/login/reset + phone code login).
- You need Dockerized `api + web + mysql` deployment with persistent data volume.
- You want a handover-ready module package with test and ops docs.

## Instructions

1. Import module payload into target project:
   - `bash "$SKILL_DIR/resources/scripts/import_module.sh" "$SKILL_DIR" "<target-project-dir>"`
2. Follow integration guide:
   - `resources/spec/INTEGRATION.md`
3. Run validation:
   - backend tests
   - target project smoke tests
4. Deploy with project-specific env and ports.
