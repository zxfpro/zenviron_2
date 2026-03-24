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



@router.get("/{tool_id}", summary="获取工具详情")
@limiter.limit(RATE_LIMIT_RULES["tool_read"] if settings.RATE_LIMIT_ENABLED else None)
def get_tool(
    request: Request,
    tool_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_scopes(["tools:read"]))
):
    """
    获取工具详细信息（包含完整Schema）

    支持两种方式：
    - 单个工具：/api/v1/tools/123
    - 多个工具：/api/v1/tools/123,456,789
    """

    if ',' in tool_id:

        try:
            tool_ids = [int(tid.strip()) for tid in tool_id.split(',')]
        except ValueError:
            return error_response('无效的工具ID格式', 400)

        if len(tool_ids) > 100:
            return error_response('一次最多支持查询100个工具', 400)

        tools = ToolService.get_tools_by_ids(db, tool_ids)
        tools_data = [tool.to_dict(include_schema=True) for tool in tools]
        return success_response(tools_data, f'成功获取 {len(tools_data)} 个工具详情')
    else:

        try:
            tool_id_int = int(tool_id)
        except ValueError:
            return error_response('无效的工具ID格式', 400)

        tool = ToolService.get_tool_by_id(db, tool_id_int)
        if not tool:
            return success_response(None,f'工具不存在：{tool_id}')
        return success_response(tool.to_dict(include_schema=True))


@router.post("", summary="创建工具", status_code=200)
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
def create_tool(
    request: Request,
    data: ToolCreateSchema,
    db: Session = Depends(get_db),
    current_user = Depends(require_scopes(["tools:write"])),
):
    """
    创建工具

    需要提供工具名称和 OpenAPI/Swagger Schema
    创建人自动从登录用户信息中获取（user.createBy）
    """
    creator = None
    if current_user and current_user.user:
        creator = current_user.user.create_by

    tool = ToolService.create_tool(
        db=db,
        name=data.name,
        schema=data.schema_,
        description=data.description,
        icon=data.icon,
        creator=creator
    )

    return success_response(tool.to_dict(include_schema=True), '工具创建成功', 200)


@router.put("/{tool_id}", summary="更新工具")
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
def update_tool(
    request: Request,
    tool_id: int,
    data: ToolUpdateSchema,
    db: Session = Depends(get_db),
    _: None = Depends(require_scopes(["tools:write"])),
):
    """更新工具信息"""
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if "schema_" in update_data:
        update_data["schema"] = update_data.pop("schema_")

    if not update_data:
        return error_response('没有需要更新的字段', 400)

    tool = ToolService.update_tool(db, tool_id, **update_data)

    return success_response(tool.to_dict(include_schema=True), '工具更新成功')


@router.delete("/{tool_id}", summary="删除工具")
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
def delete_tool(
    request: Request,
    tool_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_scopes(["tools:write"])),
):
    """删除工具"""
    ToolService.delete_tool(db, tool_id)
    return success_response(message='工具删除成功')


@router.post("/{tool_id}/enable", summary="启用工具")
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
def enable_tool(
    request: Request,
    tool_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_scopes(["tools:write"])),
):
    """启用工具"""
    tool = ToolService.enable_tool(db, tool_id)
    return success_response(tool.to_dict(), '工具已启用')


@router.post("/{tool_id}/disable", summary="停用工具")
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
def disable_tool(
    request: Request,
    tool_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_scopes(["tools:write"])),
):
    """停用工具"""
    tool = ToolService.disable_tool(db, tool_id)
    return success_response(tool.to_dict(), '工具已停用')


@router.post("/{tool_id}/test", summary="测试工具")
@limiter.limit(RATE_LIMIT_RULES["tool_test"] if settings.RATE_LIMIT_ENABLED else None)
def test_tool(
    request: Request,
    tool_id: int,
    data: ToolTestSchema,
    db: Session = Depends(get_db),
    _: None = Depends(require_scopes(["tools:execute"])),
):
    """
    测试工具

    提供测试参数，验证工具配置是否正确
    """
    result = ToolExecutor.test_tool(db, tool_id, data.parameters)

    if result['success']:
        return success_response(result['result'], '测试成功')
    else:
        return error_response(f"测试失败: {result['error']}", 500)


@router.post("/execute", summary="执行工具")
@limiter.limit(RATE_LIMIT_RULES["tool_execute"] if settings.RATE_LIMIT_ENABLED else None)
def execute_tool(
    request: Request,
    data: ToolExecuteSchema,
    db: Session = Depends(get_db),
    _: None = Depends(require_scopes(["tools:execute"]))
):
    """
    执行工具

    根据工具ID和参数执行工具
    """
    result = ToolExecutor.execute(
        db=db,
        tool_id=data.tool_id,
        parameters=data.parameters
    )

    return success_response(result, '执行成功')
