# Backend (FastAPI)

## Run

```bash
uv run uvicorn apps.backend.src.main:app --reload --port 8000
```

## API

- `GET /api/v1/llm-config`
- `PUT /api/v1/llm-config`
- `PATCH /api/v1/llm-config/providers/{provider}`
- `POST /api/v1/llm-config/providers/{provider}/test`
- `GET /api/v1/llm-config/stream`
