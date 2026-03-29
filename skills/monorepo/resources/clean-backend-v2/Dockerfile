
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    -i https://mirrors.ivolces.com/pypi/simple \
    fastapi \
    uvicorn \
    sqlmodel \
    sqlalchemy \
    pymysql \
    fastapi-users \
    fastapi-users-db-sqlmodel \
    sqladmin \
    python-multipart \
    itsdangerous \
    pytest \
    httpx \
    dotenv \
    colorlog \
    requests \
    tos \
    pydantic-settings==2.1.0

COPY app ./app
COPY main.py ./main.py

EXPOSE 9888

CMD ["python", "main.py"]
