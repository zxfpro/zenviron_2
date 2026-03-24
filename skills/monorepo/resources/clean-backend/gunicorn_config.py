"""
Gunicorn配置文件
"""
import os
import multiprocessing

# 绑定地址
bind = f"{os.getenv('SERVER_HOST', '0.0.0.0')}:{os.getenv('SERVER_PORT', '5000')}"

# Worker数量（建议：CPU核心数 * 2 + 1；可通过环境变量覆盖）
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))

# Worker类型
# FastAPI 是 ASGI 应用，Gunicorn 需要配合 UvicornWorker 才能正确处理异步请求。
worker_class = 'uvicorn.workers.UvicornWorker'

# 超时时间（秒）
timeout = int(os.getenv('GUNICORN_TIMEOUT', 60))
graceful_timeout = int(os.getenv('GUNICORN_GRACEFUL_TIMEOUT', 30))

# 保持连接时间（秒）
keepalive = 5

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 100

# 日志配置
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info').lower()

# 进程名称
proc_name = 'tool-server'

# 守护进程
daemon = False

# 预加载应用
preload_app = True

