"""
健康检查 API

用于容器/网关探活，不依赖数据库连接，避免将 `/docs` 作为健康检查目标。
"""

from fastapi import APIRouter, Request

from app.utils.response import success_response
from app.utils.rate_limit import get_limiter, RATE_LIMIT_RULES
from app.config import settings

def _get_limiter():
    """获取速率限制器，如果未初始化则使用默认配置"""
    try:
        from app.utils import rate_limit
        if hasattr(rate_limit, 'limiter') and rate_limit.limiter is not None:
            return rate_limit.limiter
    except:
        pass
    return get_limiter("memory://")

class LazyLimiter:
    """延迟加载的速率限制器包装器"""
    def __getattr__(self, name):
        limiter = _get_limiter()
        return getattr(limiter, name)
    
    def limit(self, *args, **kwargs):
        """速率限制装饰器"""
        limiter = _get_limiter()
        return limiter.limit(*args, **kwargs)

limiter = LazyLimiter()

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("", summary="健康检查")
@limiter.limit(RATE_LIMIT_RULES["health"] if settings.RATE_LIMIT_ENABLED else None)
def health_check(request: Request):
    """服务健康检查（不触发任何外部依赖）"""
    return success_response({"status": "ok"}, "ok")


