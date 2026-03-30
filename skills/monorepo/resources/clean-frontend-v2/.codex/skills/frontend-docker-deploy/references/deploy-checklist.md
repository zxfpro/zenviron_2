# Deploy Checklist

## Preflight

- Docker daemon available.
- `.env` exists and contains `APP_PORT`.
- `docker-compose.yml` points to `deploy/docker/Dockerfile`.

## Deploy

- `docker compose up -d --build`
- `docker compose ps`
- `curl -sS http://127.0.0.1:${APP_PORT:-8080}/health`

## Recovery

- `docker compose logs web --tail=200`
- `docker compose build --no-cache web`
- `docker compose up -d`
