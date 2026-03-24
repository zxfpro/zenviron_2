---
name: sql-docker
description: Set up a local PostgreSQL development service quickly with Docker Compose.
version: 0.2.5
---

# sql-docker

Skill Version: `0.2.5`

Use this skill to bootstrap and run a local PostgreSQL service from the bundled local resources in `resources/skeleton`.

## When to use

- You need a fast local SQL environment for development/testing.
- You want a reproducible Docker-based database setup.
- You want a template-backed SQL starter using Zenviron.

## Instructions

1. Preflight confirmation (must ask user before generation):
   - Confirm target base directory is `~/GitHub` (default, unless user explicitly changes it).
   - Confirm project name.
2. Resolve this skill folder path (`$SKILL_DIR`) and use fixed target base:
   - Typical install path: `~/.agents/skills/sql-docker`
   - `TARGET_DIR="$HOME/GitHub"`
   - `PROJECT_NAME="<project-name>"`
3. Copy bundled template resources to your project:
   - `mkdir -p "$TARGET_DIR"`
   - `cp -R "$SKILL_DIR/resources/skeleton" "$TARGET_DIR/$PROJECT_NAME"`
4. Initialize git repository:
   - `cd "$TARGET_DIR/$PROJECT_NAME"`
   - `git init`
5. In the generated project, copy `.env.example` to `.env`.
6. Start the service: `docker compose -f docker-compose.sql.yml up -d`.
7. Verify status: `docker compose -f docker-compose.sql.yml ps`.
8. Stop when done: `docker compose -f docker-compose.sql.yml down`.
