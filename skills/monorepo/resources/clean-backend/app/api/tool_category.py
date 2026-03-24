"""
工具分类管理API
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.extensions import get_db
from app.schemas.tool_category import (
    ToolCategoryCreateSchema,
    ToolCategoryUpdateSchema,
    ToolCategoryResponse
)
from app.services.tool_category_service import ToolCategoryService
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
        """获取速率限制器"""
        try:
            from app.utils import rate_limit
            if hasattr(rate_limit, 'limiter') and rate_limit.limiter is not None:
                return rate_limit.limiter
        except:
            pass
        return get_limiter("memory://")


limiter = LazyLimiter()

router = APIRouter(prefix="/categories", tags=["工具分类"])


@router.get("", summary="获取分类列表")
@limiter.limit(RATE_LIMIT_RULES["tool_read"] if settings.RATE_LIMIT_ENABLED else None)
def list_categories(
        request: Request,
        keyword: Optional[str] = Query(None, description="关键字（支持分类ID和分类名称搜索）"),
        status: Optional[str] = Query("all", description="状态筛选"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页大小"),
        db: Session = Depends(get_db),
        _: None = Depends(require_scopes(["tools:read"]))
):
    """
    获取工具分类列表

    - 支持按关键字（分类ID或分类名称）和状态分页查询
    """
    categories, total = ToolCategoryService.list_categories(
        db=db,
        keyword=keyword,
        status=status,
        page=page,
        page_size=page_size
    )

    category_list = []
    for category in categories:
        cat_dict = category.to_dict()
        cat_dict['tool_count'] = category.tools.count()
        category_list.append(cat_dict)

    return paginated_response(
        items=category_list,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{category_id}", summary="获取分类详情")
@limiter.limit(RATE_LIMIT_RULES["tool_read"] if settings.RATE_LIMIT_ENABLED else None)
def get_category(
        request: Request,
        category_id: int,
        page: int = Query(1, ge=1, description="工具列表页码"),
        page_size: int = Query(20, ge=1, le=100, description="工具列表每页大小"),
        db: Session = Depends(get_db),
        _: None = Depends(require_scopes(["tools:read"]))
):
    """
    获取分类详细信息（包含完整的工具列表和每个工具的详情）

    返回分类基本信息和工具列表（分页），每个工具包含完整详情
    同时返回合并后的 OpenAPI Schema，包含分类下所有工具的 paths
    """

    import logging
    logger = logging.getLogger(__name__)

    category = ToolCategoryService.get_category_by_id(db, category_id)

    tools, total_tools = ToolCategoryService.get_tools_in_category(
        db=db,
        category_id=category_id,
        page=page,
        page_size=page_size
    )

    all_tools = category.tools.filter_by(status='enabled').all()

    category_dict = category.to_dict()
    category_dict['tools'] = {
        'items': [tool.to_dict(include_schema=True) for tool in tools],  # 包含完整的工具详情（包括Schema）
        'total': total_tools,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_tools + page_size - 1) // page_size
    }
    category_dict['tool_count'] = total_tools

    merged_schema = None
    if all_tools:
        try:
            merged_schema = _merge_tool_schemas(all_tools, category)
            logger.info(f"成功合并分类 {category.name} 下 {len(all_tools)} 个工具的 Schema")
        except Exception as e:
            logger.warning(f"合并分类 {category.name} 的 Schema 时出错: {str(e)}")


    category_dict['schema'] = merged_schema

    return success_response(category_dict)


def _merge_tool_schemas(tools, category):
    """
    合并多个工具的 OpenAPI Schema 为一个完整的 Schema

    Args:
        tools: 工具对象列表
        category: 分类对象

    Returns:
        合并后的 OpenAPI Schema 字典
    """
    import copy
    import json

    if not tools:
        return None

    def _normalize_schema_to_dict(schema_value):
        """兼容 tool.schema 可能是 dict/str/None 的历史数据"""
        if schema_value is None:
            return {}
        if isinstance(schema_value, dict):
            return schema_value
        if isinstance(schema_value, str):
            try:
                parsed = json.loads(schema_value)
                return parsed if isinstance(parsed, dict) else {}
            except Exception:
                return {}
        return {}

    base_schema = copy.deepcopy(_normalize_schema_to_dict(getattr(tools[0], "schema", None)))

    if 'openapi' not in base_schema:
        base_schema['openapi'] = '3.0.0'

    if 'info' not in base_schema:
        base_schema['info'] = {}
    base_schema['info']['title'] = category.name
    base_schema['info']['description'] = category.description or f"{category.name} 工具集合"
    base_schema['info']['version'] = '1.0.0'

    if 'paths' not in base_schema:
        base_schema['paths'] = {}

    merged_paths = copy.deepcopy(base_schema['paths'])

    for tool in tools:
        tool_schema_dict = _normalize_schema_to_dict(getattr(tool, "schema", None))
        if not tool_schema_dict or 'paths' not in tool_schema_dict:
            continue

        tool_paths = tool_schema_dict.get('paths', {})
        for path, path_item in tool_paths.items():
            if path not in merged_paths:
                merged_paths[path] = {}

            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:

                    merged_paths[path][method] = copy.deepcopy(operation)

        if 'components' in tool_schema_dict:
            if 'components' not in base_schema:
                base_schema['components'] = {}

            tool_components = tool_schema_dict['components']
            for component_type in ['schemas', 'parameters', 'responses', 'requestBodies', 'headers', 'securitySchemes']:
                if component_type in tool_components:
                    if component_type not in base_schema['components']:
                        base_schema['components'][component_type] = {}

                    tool_name_prefix = tool.name.replace(' ', '_').replace('-', '_')
                    for component_name, component_def in tool_components[component_type].items():
                        prefixed_name = f"{tool_name_prefix}_{component_name}"
                        base_schema['components'][component_type][prefixed_name] = copy.deepcopy(component_def)

    base_schema['paths'] = merged_paths

    if 'servers' not in base_schema or not base_schema['servers']:
        for tool in tools:
            tool_schema_dict = _normalize_schema_to_dict(getattr(tool, "schema", None))
            if tool_schema_dict and 'servers' in tool_schema_dict and tool_schema_dict['servers']:
                base_schema['servers'] = copy.deepcopy(tool_schema_dict['servers'])
                break

        if 'servers' not in base_schema or not base_schema['servers']:
            base_schema['servers'] = [{"url": "https://api.example.com", "description": "默认服务器"}]

    return base_schema


@router.post("", summary="创建分类（可选从 OpenAPI Schema 导入工具）", status_code=200)
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
def create_category(
        request: Request,
        data: ToolCategoryCreateSchema,
        db: Session = Depends(get_db),
        current_user=Depends(require_scopes(["tools:write"]))
):
    """创建工具分类（支持三种模式）

    模式1：仅创建分类
        - 提供 name, description, icon 等基本信息

    模式2：创建分类并关联现有工具
        - 提供 name 和 tool_ids（现有工具的ID列表）

    模式3：创建分类并从 OpenAPI Schema 导入工具
        - 提供 name 和 openapi_schema
        - 可选参数 auto_split（默认为 true）
        - 会自动创建工具并关联到分类

    注意：tool_ids 和 openapi_schema 不能同时提供
    创建人自动从登录用户信息中获取（user.createBy）
    """
    import logging
    from app.services.tool_import_service import ToolImportService

    logger = logging.getLogger(__name__)

    creator = None
    if current_user and current_user.user:
        creator = current_user.user.create_by

    if not data.name or not data.name.strip():
        return error_response('工具组名称不能为空', 400)

    if data.tool_ids and data.openapi_schema:
        return error_response('tool_ids 和 openapi_schema 不能同时提供，请选择其一', 400)

    if len(data.name) > 30:
        return error_response('分类名称长度不能超过30个字符', 400)
    if data.description and len(data.description) > 100:
        return error_response('分类描述长度不能超过100个字符', 400)

    try:
        if data.openapi_schema:
            logger.info(f"开始从 OpenAPI Schema 导入工具并创建分类: {data.name}")

            import_result = ToolImportService.import_tools_from_schema(
                db=db,
                schema=data.openapi_schema,
                category_name=data.name,
                category_description=data.description,
                category_icon=data.icon,
                auto_split=data.auto_split,
                creator=creator
            )

            if import_result["category_id"]:
                category = ToolCategoryService.get_category_by_id(db, import_result["category_id"])

                cat_dict = category.to_dict()
                cat_dict['tool_count'] = category.tools.count()
                cat_dict['import_result'] = {
                    'total_tools': import_result['total_tools'],
                    'tools': import_result['tools'],
                    'errors': import_result['errors']
                }

                if import_result["errors"]:
                    message = f"分类创建成功，导入工具部分失败（成功: {import_result['total_tools']}个，失败: {len(import_result['errors'])}个）"
                else:
                    message = f"分类创建成功，已从 OpenAPI Schema 导入 {import_result['total_tools']} 个工具"

                logger.info(f"成功创建分类 {data.name}，导入 {import_result['total_tools']} 个工具")
                return success_response(cat_dict, message, 200)
            else:
                return error_response('创建分类失败：未能创建分类', 500)

        else:
            category = ToolCategoryService.create_category(
                db=db,
                name=data.name,
                description=data.description,
                icon=data.icon,
                sort_order=data.sort_order or 0,
                creator=creator,
                tool_ids=data.tool_ids
            )

            cat_dict = category.to_dict()
            cat_dict['tool_count'] = category.tools.count()

            if data.tool_ids:
                message = f'分类创建成功，已关联 {len(data.tool_ids)} 个工具'
            else:
                message = '分类创建成功'

            logger.info(f"成功创建分类: {data.name}")
            return success_response(cat_dict, message, 200)

    except BusinessException as e:
        logger.error(f"创建分类失败: {str(e)}")
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"创建分类时发生未知错误: {str(e)}")
        return error_response(f'创建分类失败: {str(e)}', 500)


@router.put("/{category_id}", summary="更新分类")
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
def update_category(
        request: Request,
        category_id: int,
        data: ToolCategoryUpdateSchema,
        db: Session = Depends(get_db),
        _: None = Depends(require_scopes(["tools:write"]))
):
    """
    更新分类信息（通过 schema 智能管理工具关联）

    通过 schema 中的 paths 智能管理工具关联关系：
    - 如果某个 path 已存在于分类中，保持关联
    - 如果某个 path 不存在于分类中，添加关联（创建新工具）
    - 如果分类下原有工具的 path 不在新 schema 中，取消关联（删除工具）
    """

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return error_response('没有需要更新的字段', 400)

    if "schema_" in update_data:
        update_data["schema"] = update_data.pop("schema_")

    category = ToolCategoryService.update_category(db, category_id, **update_data)

    cat_dict = category.to_dict()
    cat_dict['tool_count'] = category.tools.count()

    return success_response(cat_dict, '分类更新成功')


@router.delete("/{category_id}", summary="删除分类")
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
def delete_category(
        request: Request,
        category_id: int,
        delete_tools: bool = Query(True, description="是否删除关联的工具（智能删除：只删除仅属于该分类的工具）"),
        db: Session = Depends(get_db),
        _: None = Depends(require_scopes(["tools:write"]))
):
    """
    删除分类（支持智能删除工具）

    - delete_tools=true: 智能删除，只删除仅属于该分类的工具
    - delete_tools=false: 只删除分类和关联关系，保留所有工具
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        result = ToolCategoryService.delete_category(db, category_id, delete_tools=delete_tools)

        if result.get('success'):
            message = f'分类删除成功（删除工具: {result["deleted_tools"]}个，保留工具: {result["kept_tools"]}个）'
            return success_response(
                data=result,
                message=message
            )
        else:
            logger.warning(f"删除分类失败: {result.get('message')}")
            return {
                'code': 200,
                'data': result
            }
    except BusinessException as e:
        logger.error(f"删除分类失败: {str(e)}")
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"删除分类时发生未知错误: {str(e)}")
        return error_response(f'删除分类失败: {str(e)}', 500)


@router.post("/{category_id}/enable", summary="启用分类")
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
def enable_category(
        request: Request,
        category_id: int,
        db: Session = Depends(get_db),
        _: None = Depends(require_scopes(["tools:write"]))
):
    """启用分类"""
    category = ToolCategoryService.enable_category(db, category_id)
    return success_response(category.to_dict(), '分类已启用')


@router.post("/{category_id}/disable", summary="停用分类")
@limiter.limit(RATE_LIMIT_RULES["tool_write"] if settings.RATE_LIMIT_ENABLED else None)
def disable_category(
        request: Request,
        category_id: int,
        db: Session = Depends(get_db),
        _: None = Depends(require_scopes(["tools:write"]))
):
    """停用分类"""
    import logging
    logger = logging.getLogger(__name__)

    try:
        result = ToolCategoryService.disable_category(db, category_id)

        if result.get('success'):
            return success_response(
                data=result,
                message='分类已停用'
            )
        else:
            logger.warning(f"停用分类失败: {result.get('message')}")
            return {
                'code': 200,
                'data': result
            }
    except BusinessException as e:
        logger.error(f"停用分类失败: {str(e)}")
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"停用分类时发生未知错误: {str(e)}")
        return error_response(f'停用分类失败: {str(e)}', 500)




