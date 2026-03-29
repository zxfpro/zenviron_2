FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY apps/backend/src ./apps/backend/src

RUN pip install --no-cache-dir uv && uv sync --frozen

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "kanban_api.main:app", "--app-dir", "apps/backend/src", "--host", "0.0.0.0", "--port", "8001"]

