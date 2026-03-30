---
name: frontend-docker-deploy
description: Build, run, and troubleshoot Docker deployment for this frontend project with Nginx and health checks. Use when setting up containerized delivery, validating runtime behavior, debugging compose failures, or verifying production-like deployment locally.
---

# Frontend Docker Deploy

Operate container deployment for the current frontend stack.

## Deployment Workflow

1. Verify `deploy/docker/Dockerfile`, Nginx config, and `docker-compose.yml` are aligned.
2. Initialize env with `./scripts/init.sh` if missing.
3. Run `docker compose up -d --build`.
4. Validate `/health` and static page routing.
5. Inspect logs and container health when failures happen.

## Troubleshooting Order

1. Check `docker compose ps` and health status.
2. Check `docker compose logs web --tail=200`.
3. Confirm Nginx `/health` and `try_files` behavior.
4. Rebuild image without cache when stale artifacts are suspected.

## Expected Outputs

- Container running with healthy status.
- `GET /health` returns JSON with status `ok`.
- SPA refresh on nested routes still loads `index.html`.

## References and Scripts

- Read `references/deploy-checklist.md` for full checks.
- Use `scripts/check-health.sh` for quick health verification.
