这里用来存放数据结构 定义

```python

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



```