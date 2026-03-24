"""
工具导入 API
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.extensions import get_db
from app.schemas.tool_import import (
    ToolImportResultSchema,
    SchemaPreviewSchema,
    SchemaPreviewResultSchema,
    ToolTestSchema,
    ToolBatchSaveSchema
)
from app.services.tool_import_service import ToolImportService
from app.security.token_auth import require_scopes
from app.utils.response import success_response, error_response
from app.utils.exceptions import BusinessException, InvalidSchemaException
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
        """获取速率限制器"""
        try:
            from app.utils import rate_limit
            if hasattr(rate_limit, 'limiter') and rate_limit.limiter is not None:
                return rate_limit.limiter
        except:
            pass
        return get_limiter("memory://")

limiter = LazyLimiter()

router = APIRouter(prefix="/tools", tags=["工具导入"])


@router.post("/preview-schema", summary="预览 OpenAPI Schema（不保存）", status_code=200)
@limiter.limit(RATE_LIMIT_RULES["tool_read"] if settings.RATE_LIMIT_ENABLED else None)
def preview_schema(
    request: Request,
    data: SchemaPreviewSchema,
    _: None = Depends(require_scopes(["tools:read"]))
):
    """
    预览 OpenAPI Schema，返回解析后的工具列表（不保存到数据库）
    
    前端可以使用此接口：
    1. 上传 Schema 后立即查看将要创建的工具列表
    2. 在保存前测试工具
    3. 选择性地保存某些工具
    
    支持两种模式：
    - auto_split=true: 解析为多个独立工具
    - auto_split=false: 解析为单个工具包含所有操作
    """
    try:
        result = ToolImportService.preview_schema(
            schema=data.schema_,
            auto_split=data.auto_split
        )

        message = f"解析成功，共 {result['total_tools']} 个工具"
        return success_response(result, message, 200)
    
    except InvalidSchemaException as e:
        return error_response(f"Schema 验证失败: {str(e)}", 400)
    except Exception as e:
        return error_response(f"解析失败: {str(e)}", 500)


@router.post("/test-tool", summary="测试工具（在保存前测试）", status_code=200)
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
async def test_tool(
    request: Request,
    data: ToolTestSchema,
    _: None = Depends(require_scopes(["tools:write"]))
):
    """
    测试工具（在保存前测试 API 调用）
    
    前端可以使用此接口在保存工具前验证：
    1. API 端点是否可访问
    2. 参数是否正确
    3. 响应格式是否符合预期
    """
    try:
        result = await ToolImportService.test_tool(
            schema=data.schema_,
            parameters=data.parameters
        )

        if result["success"]:
            message = f"测试成功 (HTTP {result['status_code']})"
        else:
            message = f"测试失败: {result['error']}"

        return success_response(result, message, 200)
    
    except BusinessException as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"测试失败: {str(e)}", 500)


@router.post("/batch-save", summary="批量保存工具", status_code=200)
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
def batch_save_tools(
    request: Request,
    data: ToolBatchSaveSchema,
    db: Session = Depends(get_db),
    current_user = Depends(require_scopes(["tools:write"]))
):
    """
    批量保存已解析的工具到数据库

    前端工作流程：
    1. 调用 /preview-schema 预览工具列表
    2. 用户选择要保存的工具
    3. 可选：调用 /test-tool 测试工具
    4. 调用此接口保存选中的工具到数据库

    可选地创建或关联到分类。
    """
    if data.category_name is not None:
        if not data.category_name or not data.category_name.strip():
            return error_response('工具组名称不能为空', 400)

    if current_user and current_user.user:
        creator = current_user.user.create_by
    else:
        creator = None

    try:
        result = ToolImportService.batch_save_tools(
            db=db,
            tools=data.tools,
            category_name=data.category_name,
            category_description=data.category_description,
            category_icon=data.category_icon,
            creator=creator
        )

        if result["errors"]:
            message = f"保存完成（成功: {result['total_tools']}个，失败: {len(result['errors'])}个）"
        else:
            message = f"保存成功，创建了 {result['total_tools']} 个工具"

        if result["category_name"]:
            message += f"，已关联到分类: {result['category_name']}"

        return success_response(result, message, 200)

    except BusinessException as e:
        return error_response(str(e), 500)
    except Exception as e:
        return error_response(f"保存失败: {str(e)}", 500)
