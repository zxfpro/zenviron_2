# Docker Deployment

## 1. Initialize

```bash
./scripts/init.sh
```

## 2. Build and run

```bash
docker compose up -d --build
```

## 3. Verify

```bash
curl -sS http://127.0.0.1:${APP_PORT:-8080}/health
```

Expected response example:

```json
{"status":"ok","service":"clean-frontend-v2","version":"0.1.0","timestamp":"2026-03-30T15:00:00+00:00"}
```

## 4. Stop

```bash
docker compose down
```
