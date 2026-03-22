# SQL Docker Bootstrap Skill

Use this skill to quickly start a local PostgreSQL service via Docker Compose.

## Responsibilities
- Provide ready-to-run SQL Docker files.
- Keep local DB setup reproducible for AI-driven development.
- Avoid leaking credentials by using `.env.example`.

## Quick Start

```bash
cp .env.example .env
docker compose -f docker-compose.sql.yml up -d
```

## Health Check

```bash
docker compose -f docker-compose.sql.yml ps
```

## Stop

```bash
docker compose -f docker-compose.sql.yml down
```

## Notes
- Data persists in volume `zenviron_postgres_data`.
- Default container: `{{ REPO_SLUG }}-postgres`.
