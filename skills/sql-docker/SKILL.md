---
name: sql-docker
description: Set up a local PostgreSQL development service quickly with Docker Compose.
---

# sql-docker

Use this skill to bootstrap and run a local PostgreSQL service from `template/sql-docker/skeleton`.

## When to use

- You need a fast local SQL environment for development/testing.
- You want a reproducible Docker-based database setup.
- You want a template-backed SQL starter using Zenviron.

## Instructions

1. Run `uv run zenviron init "<project_name>" --template sql-docker`.
2. In the generated project, copy `.env.example` to `.env`.
3. Start the service: `docker compose -f docker-compose.sql.yml up -d`.
4. Verify status: `docker compose -f docker-compose.sql.yml ps`.
5. Stop when done: `docker compose -f docker-compose.sql.yml down`.
