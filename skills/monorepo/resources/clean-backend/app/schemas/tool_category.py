"""
工具分类相关 Schema
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any


class ToolCategoryCreateSchema(BaseModel):
    """创建工具分类请求 Schema

    支持两种创建方式：
    1. 仅创建分类：提供 name, description, icon 等基本信息，可选择关联现有工具（tool_ids）
    2. 创建分类并从 OpenAPI Schema 导入工具：提供 openapi_schema 和 auto_split 参数

    注意：creator 字段会自动从登录用户信息中获取（user.createBy），无需前端传入
    """
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "天气工具",
                    "description": "获取天气信息的工具集合",
                    "icon": "🌤️",
                    "sort_order": 0,
                    "openapi_schema": {
                        "openapi": "3.0.0",
                        "info": {"title": "Weather API", "version": "1.0.0"},
                        "servers": [{"url": "https://api.weather.com"}],
                        "paths": {
                            "/weather": {
                                "get": {
                                    "summary": "获取天气",
                                    "operationId": "getWeather",
                                    "responses": {"200": {"description": "成功"}}
                                }
                            }
                        }
                    },
                    "auto_split": True
                }
            ]
        }
    )
    
    name: str = Field(..., max_length=50, description="分类名称")
    description: Optional[str] = Field(None, max_length=200, description="分类描述")
    icon: Optional[str] = Field(None, max_length=255, description="分类图标URL或Emoji")
    sort_order: Optional[int] = Field(0, description="排序顺序")
    tool_ids: Optional[List[int]] = Field(None, description="关联的现有工具ID列表（与 openapi_schema 二选一）")
    openapi_schema: Optional[Dict[str, Any]] = Field(None, description="OpenAPI Schema（用于自动导入工具）")
    auto_split: bool = Field(True, description="是否自动拆分成多个工具（仅当提供 openapi_schema 时有效）")


class ToolPathInfo(BaseModel):
    """工具路径信息（用于智能合并）"""
    model_config = ConfigDict(populate_by_name=True)

    path: str = Field(..., description="工具的API路径")
    method: Optional[str] = Field(None, description="HTTP方法（GET/POST/PUT/DELETE等）")
    tool_id: Optional[int] = Field(None, description="如果工具已存在，提供工具ID；否则需要提供schema创建新工具")
    schema_: Optional[Dict[str, Any]] = Field(None, alias="schema", description="如果工具不存在，提供schema创建新工具")


class ToolCategoryUpdateSchema(BaseModel):
    """更新工具分类请求 Schema

    通过 schema 中的 paths 智能管理工具关联关系：
    - 如果某个 path 已存在于分类中，保持关联
    - 如果某个 path 不存在于分类中，添加关联（创建新工具）
    - 如果分类下原有工具的 path 不在新 schema 中，取消关联
    """
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "天气工具",
                    "description": "获取天气信息的工具集合",
                    "schema": {
                        "openapi": "3.0.0",
                        "info": {"title": "Weather API", "version": "1.0.0"},
                        "servers": [{"url": "https://api.weather.com"}],
                        "paths": {
                            "/api/weather": {
                                "get": {
                                    "summary": "获取天气",
                                    "operationId": "getWeather",
                                    "responses": {"200": {"description": "成功"}}
                                }
                            },
                            "/api/forecast": {
                                "post": {
                                    "summary": "获取天气预报",
                                    "operationId": "getForecast",
                                    "responses": {"200": {"description": "成功"}}
                                }
                            }
                        }
                    }
                }
            ]
        }
    )

    name: Optional[str] = Field(None, max_length=50, description="分类名称")
    description: Optional[str] = Field(None, max_length=200, description="分类描述")
    schema_: Optional[Dict[str, Any]] = Field(None, alias="schema", description="OpenAPI Schema（用于智能管理工具关联）")


class ToolCategoryResponse(BaseModel):
    """工具分类响应 Schema"""
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    status: str
    sort_order: int
    creator: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    tool_count: Optional[int] = Field(None, description="分类下的工具数量")



