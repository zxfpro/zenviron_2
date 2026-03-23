---
name: sql-docker
description: Set up a local PostgreSQL development service quickly with Docker Compose.
version: 0.2.1
---

# sql-docker

Skill Version: `0.2.1`

Use this skill to bootstrap and run a local PostgreSQL service from the bundled local resources in `resources/skeleton`.

## When to use

- You need a fast local SQL environment for development/testing.
- You want a reproducible Docker-based database setup.
- You want a template-backed SQL starter using Zenviron.

## Instructions

1. Preflight confirmation (must ask user before generation):
   - Confirm target base directory is `~/GitHub` (default, unless user explicitly changes it).
   - Confirm project name.
   - Confirm GitHub auth readiness:
     - `GITHUB_TOKEN` or `GH_TOKEN` exists in environment, or
     - `gh auth status` is already valid.
2. Preflight self-check commands (run automatically when possible):
   - `printenv GITHUB_TOKEN >/dev/null && echo GITHUB_TOKEN_OK || echo GITHUB_TOKEN_MISSING`
   - `printenv GH_TOKEN >/dev/null && echo GH_TOKEN_OK || echo GH_TOKEN_MISSING`
   - `gh auth status` (if `gh` is installed)
3. If required auth is missing, stop and ask user to configure it before continuing.
4. Resolve this skill folder path (`$SKILL_DIR`) and use fixed target base:
   - Typical install path: `~/.agents/skills/sql-docker`
   - `TARGET_DIR="$HOME/GitHub"`
   - `PROJECT_NAME="<project-name>"`
5. Copy bundled template resources to your project:
   - `mkdir -p "$TARGET_DIR"`
   - `cp -R "$SKILL_DIR/resources/skeleton" "$TARGET_DIR/$PROJECT_NAME"`
6. In the generated project, copy `.env.example` to `.env`.
7. Start the service: `docker compose -f docker-compose.sql.yml up -d`.
8. Verify status: `docker compose -f docker-compose.sql.yml ps`.
9. Stop when done: `docker compose -f docker-compose.sql.yml down`.
