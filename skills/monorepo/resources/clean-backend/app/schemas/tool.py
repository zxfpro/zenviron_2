"""
工具相关Schema定义（Pydantic）
"""
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.config import ConfigDict
import json


class ToolCreateSchema(BaseModel):
    """创建工具请求Schema"""
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=30, description="工具名称")
    description: Optional[str] = Field(None, max_length=100, description="工具描述")
    schema_: str = Field(..., alias="schema", description="OpenAPI/Swagger Schema JSON字符串")
    icon: Optional[str] = Field(None, description="工具图标URL")

    @field_validator('schema_')
    @classmethod
    def validate_schema(cls, v: str) -> str:
        """验证Schema是否为有效的JSON"""
        try:
            schema_dict = json.loads(v)
            if not isinstance(schema_dict, dict):
                raise ValueError('Schema必须是JSON对象')
            return v
        except json.JSONDecodeError as e:
            raise ValueError(f'Schema必须是有效的JSON格式: {str(e)}')


class ToolUpdateSchema(BaseModel):
    """更新工具请求Schema"""
    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = Field(None, min_length=1, max_length=30, description="工具名称")
    description: Optional[str] = Field(None, max_length=100, description="工具描述")
    schema_: Optional[str] = Field(None, alias="schema", description="OpenAPI/Swagger Schema JSON字符串")
    icon: Optional[str] = Field(None, description="工具图标URL")
    
    @field_validator('schema_')
    @classmethod
    def validate_schema(cls, v: Optional[str]) -> Optional[str]:
        """验证Schema是否为有效的JSON"""
        if v is None:
            return v
        try:
            schema_dict = json.loads(v)
            if not isinstance(schema_dict, dict):
                raise ValueError('Schema必须是JSON对象')
            return v
        except json.JSONDecodeError as e:
            raise ValueError(f'Schema必须是有效的JSON格式: {str(e)}')


class ToolQuerySchema(BaseModel):
    """工具查询请求Schema"""
    keyword: Optional[str] = Field(None, description="关键字")
    status: Optional[Literal['enabled', 'disabled', 'all']] = Field('all', description="状态筛选")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页大小")


class ToolExecuteSchema(BaseModel):
    """工具执行请求Schema"""
    tool_id: int = Field(..., description="工具ID")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="工具参数")


class ToolTestSchema(BaseModel):
    """
    工具测试请求 Schema

    兼容两种 body 形式：
    1) {"parameters": {...}}   （推荐）
    2) {...}                  （历史/简化写法，会自动包裹为 parameters）
    """

    parameters: Dict[str, Any] = Field(default_factory=dict, description="工具参数")

    @model_validator(mode="before")
    @classmethod
    def normalize_body(cls, data: Any):
        """将不带 parameters 的 dict 输入自动包裹，避免调用方格式差异导致缺参"""
        if isinstance(data, dict) and "parameters" not in data:
            return {"parameters": data}
        return data


class ToolResponse(BaseModel):
    """工具响应Schema"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    status: str
    creator: Optional[str]
    created_at: str
    updated_at: str
    schema_: Optional[Dict[str, Any]] = Field(default=None, alias="schema")


class ToolListResponse(BaseModel):
    """工具列表响应Schema"""
    items: list[ToolResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

