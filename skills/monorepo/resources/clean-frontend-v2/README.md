# clean-frontend-v2

A minimal, production-ready frontend starter based on React + TypeScript + Vite.

## Stack

- React 18
- TypeScript 5
- Vite 5
- Nginx (for container runtime)

## Quick start (local)

```bash
npm install
npm run dev
```

Open: `http://127.0.0.1:3000`

## Health endpoint

- Local dev (Vite): `http://127.0.0.1:3000/health` is not provided by Vite by default.
- Docker runtime (Nginx): `http://127.0.0.1:8080/health` returns runtime health JSON.

## Docker deployment

```bash
./scripts/init.sh
docker compose up -d --build
curl -sS http://127.0.0.1:${APP_PORT:-8080}/health
```

More details: `docs/deployment.md`

## Scripts

```bash
npm run dev        # Start local dev server
npm run build      # Type-check + production build
npm run preview    # Preview build output
npm run typecheck  # Run TypeScript checks only
```

## Project structure

See `PROJECT_STRUCTURE.md` for full directory conventions.
