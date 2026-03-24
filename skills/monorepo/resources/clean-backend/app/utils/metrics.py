"""
Prometheus Metrics 配置
"""
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
from fastapi import FastAPI

logger = logging.getLogger(__name__)

# 自定义指标
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

rate_limit_hits_total = Counter(
    'rate_limit_hits_total',
    'Total rate limit hits',
    ['endpoint', 'ip']
)

database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections'
)

database_connections_idle = Gauge(
    'database_connections_idle',
    'Idle database connections'
)


def setup_prometheus_metrics(app: FastAPI):
    """
    设置 Prometheus metrics
    
    Args:
        app: FastAPI 应用实例
    """
    try:
        # 使用 prometheus-fastapi-instrumentator 自动收集指标
        instrumentator = Instrumentator(
            should_group_status_codes=False,
            should_ignore_untemplated=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/metrics", "/health", "/docs", "/redoc", "/openapi.json"],
            inprogress_name="http_requests_inprogress",
            inprogress_labels=True,
        )
        
        instrumentator.instrument(app)
        instrumentator.expose(app)
        
        logger.info("Prometheus metrics 已启用 - /metrics 端点已暴露")
        
    except Exception as e:
        logger.error(f"Prometheus metrics 设置失败: {str(e)}", exc_info=True)
        # 不阻断应用启动，监控是可选的

