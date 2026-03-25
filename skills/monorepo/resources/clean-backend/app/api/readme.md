这里用来存放对外的API 服务 
open router 示例如下




```python

"""
工具管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.extensions import get_db
from app.schemas.tool import (
    ToolCreateSchema,
    ToolUpdateSchema,
    ToolQuerySchema,
    ToolExecuteSchema,
    ToolTestSchema,
    ToolResponse,
    ToolListResponse
)
from app.services.tool_service import ToolService
from app.services.tool_executor import ToolExecutor
from app.security.token_auth import require_scopes
from app.utils.response import success_response, error_response, paginated_response
from app.utils.exceptions import BusinessException
from app.utils.rate_limit import get_limiter, RATE_LIMIT_RULES
from app.config import settings


class LazyLimiter:
    """延迟加载的速率限制器包装器"""
    def __getattr__(self, name):
        limiter = self._get_limiter()
        return getattr(limiter, name)

    def limit(self, *args, **kwargs):
        """速率限制装饰器"""
        limiter = self._get_limiter()
        return limiter.limit(*args, **kwargs)

    def _get_limiter(self):
        """获取速率限制器，如果未初始化则使用默认配置"""
        try:
            from app.utils import rate_limit
            if hasattr(rate_limit, 'limiter') and rate_limit.limiter is not None:
                return rate_limit.limiter
        except:
            pass
        return get_limiter("memory://")

limiter = LazyLimiter()

router = APIRouter(prefix="/tools", tags=["工具管理"])


@router.get("", summary="获取工具列表")
@limiter.limit(RATE_LIMIT_RULES["tool_read"] if settings.RATE_LIMIT_ENABLED else None)
def list_tools(
    request: Request,
    keyword: Optional[str] = Query(None, description="关键字"),
    status: Optional[str] = Query("all", description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db),
    _: None = Depends(require_scopes(["tools:read"]))
):
    """
    获取工具列表

    支持分页和筛选
    """
    tools, total = ToolService.list_tools(
        db=db,
        keyword=keyword,
        status=status,
        page=page,
        page_size=page_size
    )

    # 转换为字典
    tool_list = [tool.to_dict() for tool in tools]

    return paginated_response(
        items=tool_list,
        total=total,
        page=page,
        page_size=page_size
    )



```