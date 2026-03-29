FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
COPY README.md /app/README.md
COPY apps /app/apps

RUN pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --extra-index-url https://mirrors.aliyun.com/pypi/simple \
    --default-timeout=120 \
    -e .

EXPOSE 8000

CMD ["uvicorn", "apps.backend.login_m_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
