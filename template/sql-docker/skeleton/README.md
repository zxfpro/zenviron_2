# {{ PROJECT_NAME }} SQL Docker

This template provides a local PostgreSQL runtime via Docker.

## Start

```bash
cp .env.example .env
docker compose -f docker-compose.sql.yml up -d
```

## Connection

- Host: `localhost`
- Port: `5432`
- User: from `.env`
- Password: from `.env`
- Database: from `.env`
