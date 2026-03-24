"""
ASGI入口文件（兼容保留旧文件名 `wsgi.py`）

说明：
- FastAPI 是 ASGI 应用，不应使用 Flask 的 `app.run()` 启动方式
- 生产环境推荐：`gunicorn -c gunicorn_config.py main:app`
- 本文件仅提供 `app` 变量，便于某些部署/IDE 配置引用（如 `wsgi:app`）
"""
from dotenv import load_dotenv
from app import create_app

# 加载 .env 文件（如果存在）
load_dotenv()

# 创建应用实例
app = create_app()

