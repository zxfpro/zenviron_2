"""
工具导入相关 Schema
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any


class ToolImportSchema(BaseModel):
    """从 OpenAPI Schema 导入工具请求 Schema"""
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "schema": {
                    "openapi": "3.0.0",
                    "info": {
                        "title": "My API",
                        "version": "1.0.0"
                    },
                    "servers": [{"url": "https://api.example.com"}],
                    "paths": {
                        "/users": {
                            "get": {
                                "summary": "获取用户列表",
                                "operationId": "getUsers",
                                "responses": {
                                    "200": {"description": "成功"}
                                }
                            }
                        }
                    }
                }
            }
        }
    )

    schema_: Dict[str, Any] = Field(..., alias="schema", description="完整的 OpenAPI/Swagger Schema")
    category_name: Optional[str] = Field(None, description="分类名称（可选，如果提供会创建或使用该分类）")
    category_description: Optional[str] = Field(None, description="分类描述（可选）")
    category_icon: Optional[str] = Field(None, description="分类图标（可选，如：🔑）")
    auto_split: bool = Field(True, description="是否自动拆分成多个工具（可选，默认：true）")


class ToolImportResultSchema(BaseModel):
    """工具导入结果 Schema"""
    category_id: Optional[int] = Field(None, description="分类ID")
    category_name: Optional[str] = Field(None, description="分类名称")
    tools: list[Dict[str, Any]] = Field(..., description="创建的工具列表")
    total_tools: int = Field(..., description="创建的工具总数")
    errors: list[str] = Field(default_factory=list, description="错误列表（如果有）")


class SchemaPreviewSchema(BaseModel):
    """Schema 预览请求 Schema"""
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "schema": {
                    "openapi": "3.0.0",
                    "info": {
                        "title": "My API",
                        "version": "1.0.0"
                    },
                    "servers": [{"url": "https://api.example.com"}],
                    "paths": {
                        "/users": {
                            "get": {
                                "summary": "获取用户列表",
                                "operationId": "getUsers"
                            }
                        }
                    }
                }
            }
        }
    )

    schema_: Dict[str, Any] = Field(..., alias="schema", description="完整的 OpenAPI/Swagger Schema")
    auto_split: bool = Field(True, description="是否自动拆分成多个工具（默认：true）")


class ToolPreviewItemSchema(BaseModel):
    """工具预览项 Schema"""
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., description="工具名称")
    description: Optional[str] = Field(None, description="工具描述")
    method: str = Field(..., description="HTTP 方法")
    path: str = Field(..., description="API 路径")
    operation_id: str = Field(..., description="操作ID")
    summary: Optional[str] = Field(None, description="操作摘要")
    schema_: Dict[str, Any] = Field(..., alias="schema", description="工具的完整 Schema")
    parameters: list[Dict[str, Any]] = Field(default_factory=list, description="参数列表")


class SchemaPreviewResultSchema(BaseModel):
    """Schema 预览结果 Schema"""
    total_tools: int = Field(..., description="工具总数")
    tools: list[ToolPreviewItemSchema] = Field(..., description="工具列表")
    base_info: Dict[str, Any] = Field(..., description="基础信息（title, version, servers等）")


class ToolTestSchema(BaseModel):
    """工具测试请求 Schema"""
    model_config = ConfigDict(populate_by_name=True)

    schema_: Dict[str, Any] = Field(..., alias="schema", description="工具的 OpenAPI Schema")
    parameters: Optional[Dict[str, Any]] = Field(None, description="测试参数")


class ToolBatchSaveSchema(BaseModel):
    """批量保存工具请求 Schema"""
    tools: list[Dict[str, Any]] = Field(..., description="要保存的工具列表，每个包含 name, schema, description")
    category_name: Optional[str] = Field(None, description="分类名称（可选）")
    category_description: Optional[str] = Field(None, description="分类描述（可选）")
    category_icon: Optional[str] = Field(None, description="分类图标（可选）")

