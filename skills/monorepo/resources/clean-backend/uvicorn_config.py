"""
Uvicorn配置文件（生产环境）
"""
import os
import multiprocessing

# 绑定地址
bind = f"{os.getenv('SERVER_HOST', '0.0.0.0')}:{os.getenv('SERVER_PORT', '5000')}"

# Worker数量
workers = int(os.getenv('UVICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))

# Worker类
worker_class = 'uvicorn.workers.UvicornWorker'

# 超时时间（秒）
timeout = int(os.getenv('UVICORN_TIMEOUT', 60))

# 保持连接时间（秒）
keepalive = 5

# 日志配置
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info').lower()

# 进程名称
proc_name = 'tool-server-fastapi'

# 守护进程
daemon = False

# 预加载应用
preload_app = True

