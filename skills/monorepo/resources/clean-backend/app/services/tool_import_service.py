"""
工具导入服务
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Tuple, Optional
import json
import logging
import re
import httpx

from app.services.tool_service import ToolService
from app.services.tool_category_service import ToolCategoryService
from app.utils.exceptions import BusinessException, InvalidSchemaException

logger = logging.getLogger(__name__)


class ToolImportService:
    """工具导入服务"""
    
    @staticmethod
    def _generate_tool_name_from_path(path: str, method: str) -> str:
        """
        根据 path 和 method 生成工具名称
        
        例如：
        - path: /system/apiKey/list, method: get -> systemapiKeylist_get
        - path: /user/info, method: post -> userinfo_post
        - path: /api/v1/users/{id}, method: delete -> apiv1usersid_delete
        
        Args:
            path: API 路径
            method: HTTP 方法
            
        Returns:
            生成的工具名称
        """
        clean_path = path.strip('/')

        clean_path = re.sub(r'\{(\w+)\}', r'\1', clean_path)

        name_parts = clean_path.replace('/', '')

        tool_name = f"{name_parts}_{method.lower()}"

        return tool_name[:30]
    
    @staticmethod
    def preview_schema(schema: Dict[str, Any], auto_split: bool = True) -> Dict[str, Any]:
        """
        预览 OpenAPI Schema，返回解析后的工具列表（不保存到数据库）
        
        Args:
            schema: 完整的 OpenAPI Schema
            auto_split: 是否自动拆分成多个工具
            
        Returns:
            预览结果，包含：
            - total_tools: 工具总数
            - tools: 工具列表
            - base_info: 基础信息
            
        Raises:
            InvalidSchemaException: Schema 格式无效
        """

        operations = ToolImportService.extract_operations_from_schema(schema)

        base_info = {
            "openapi": schema.get("openapi", "3.0.0"),
            "title": schema.get("info", {}).get("title", "未命名API"),
            "version": schema.get("info", {}).get("version", "1.0.0"),
            "description": schema.get("info", {}).get("description", ""),
            "servers": schema.get("servers", [])
        }

        tools_preview = []
        
        if not auto_split:
            tool_preview = {
                "name": base_info["title"][:30],
                "description": base_info["description"][:100] if base_info["description"] else None,
                "method": "MULTIPLE",
                "path": "MULTIPLE",
                "operation_id": "combined",
                "summary": base_info["title"],
                "schema": schema,
                "parameters": [],
                "operation_count": len(operations)
            }
            tools_preview.append(tool_preview)
        else:
            for op in operations:
                tool_schema = {
                    "openapi": base_info["openapi"],
                    "info": {
                        "title": op["summary"] if op["summary"] else f"{op['method'].upper()} {op['path']}",
                        "version": base_info["version"],
                        "description": op["description"]
                    },
                    "servers": base_info["servers"],
                    "paths": {
                        op["path"]: {
                            op["method"]: op["operation"]
                        }
                    }
                }

                if "components" in schema:
                    tool_schema["components"] = schema["components"]

                if op["summary"]:
                    tool_name = op["summary"][:30]
                elif op["operation_id"] and op["operation_id"] != "combined":
                    tool_name = op["operation_id"][:30]
                else:
                    tool_name = ToolImportService._generate_tool_name_from_path(op["path"], op["method"])

                parameters = []
                operation_obj = op["operation"]

                if "parameters" in operation_obj:
                    for param in operation_obj["parameters"]:
                        parameters.append({
                            "name": param.get("name"),
                            "in": param.get("in"),
                            "description": param.get("description", ""),
                            "required": param.get("required", False),
                            "schema": param.get("schema", {})
                        })

                if "requestBody" in operation_obj:
                    parameters.append({
                        "name": "requestBody",
                        "in": "body",
                        "description": operation_obj["requestBody"].get("description", "请求体"),
                        "required": operation_obj["requestBody"].get("required", False),
                        "schema": operation_obj["requestBody"].get("content", {})
                    })

                tool_preview = {
                    "name": tool_name,
                    "description": op["description"][:100] if op["description"] else None,
                    "method": op["method"].upper(),
                    "path": op["path"],
                    "operation_id": op["operation_id"],
                    "summary": op["summary"],
                    "schema": tool_schema,
                    "parameters": parameters
                }
                tools_preview.append(tool_preview)

        return {
            "total_tools": len(tools_preview),
            "tools": tools_preview,
            "base_info": base_info
        }

    @staticmethod
    def extract_operations_from_schema(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从 OpenAPI Schema 中提取所有操作

        Args:
            schema: 完整的 OpenAPI Schema

        Returns:
            操作列表，每个操作包含：
            - path: 路径
            - method: HTTP 方法
            - operation: 操作定义
            - operation_id: 操作ID
            - summary: 操作摘要

        Raises:
            InvalidSchemaException: Schema 格式无效
        """

        if not isinstance(schema, dict):
            raise InvalidSchemaException("Schema 必须是一个对象")

        if "info" not in schema or not isinstance(schema["info"], dict):
            raise InvalidSchemaException("Schema 缺少 'info' 字段或 info 不是对象")

        if "servers" not in schema or not isinstance(schema["servers"], list):
            raise InvalidSchemaException("Schema 缺少 'servers' 字段或 servers 不是数组")

        servers = schema.get("servers", [])
        if not servers:
            raise InvalidSchemaException("servers 数组不能为空")

        has_valid_server = False
        for server in servers:
            if not isinstance(server, dict):
                continue
            url = server.get("url", "").strip()
            if url:
                has_valid_server = True
                break

        if not has_valid_server:
            raise InvalidSchemaException("servers 数组中必须包含至少一个包含有效 url 的对象")

        if "paths" not in schema or not isinstance(schema["paths"], dict):
            raise InvalidSchemaException("Schema 缺少 'paths' 字段或 paths 不是对象")

        operations = []
        paths = schema.get("paths", {})

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            http_methods = ["get", "post", "put", "delete", "patch", "head", "options"]
            for method in http_methods:
                if method not in path_item:
                    continue

                operation = path_item[method]
                if not isinstance(operation, dict):
                    continue

                if operation.get("operationId"):
                    operation_id = operation.get("operationId")
                else:

                    clean_path = path.strip('/')
                    clean_path = re.sub(r'\{(\w+)\}', r'\1', clean_path)
                    name_parts = clean_path.replace('/', '')
                    operation_id = f"{name_parts}_{method}"
                summary = operation.get("summary", None)  # 先不设置默认值
                description = operation.get("description", summary if summary else f"{method.upper()} {path}")

                operations.append({
                    "path": path,
                    "method": method,
                    "operation": operation,
                    "operation_id": operation_id,
                    "summary": summary,  # 可能是 None
                    "description": description
                })

        if not operations:
            raise InvalidSchemaException("Schema 中没有找到任何操作")

        return operations

    @staticmethod
    def create_tool_from_operation(
        db: Session,
        base_schema: Dict[str, Any],
        path: str,
        method: str,
        operation: Dict[str, Any],
        operation_id: str,
        summary: str,
        description: str,
        creator: Optional[str] = None
    ) -> Any:
        """
        从单个操作创建工具

        Args:
            db: 数据库会话
            base_schema: 基础 Schema（包含 openapi, info, servers 等）
            path: 路径
            method: HTTP 方法
            operation: 操作定义
            operation_id: 操作ID
            summary: 操作摘要
            description: 操作描述
            creator: 创建人

        Returns:
            创建的工具对象
        """
        # 构建单个工具的 Schema
        tool_schema = {
            "openapi": base_schema.get("openapi", "3.0.0"),
            "info": {
                "title": summary,
                "version": base_schema.get("info", {}).get("version", "1.0.0"),
                "description": description
            },
            "servers": base_schema.get("servers", []),
            "paths": {
                path: {
                    method: operation
                }
            }
        }

        if "components" in base_schema:
            tool_schema["components"] = base_schema["components"]

        if summary:
            tool_name = summary[:30]
        elif operation_id and operation_id != "combined":
            tool_name = operation_id[:30]
        else:
            tool_name = ToolImportService._generate_tool_name_from_path(path, method)

        tool = ToolService.create_tool(
            db=db,
            name=tool_name,
            schema=json.dumps(tool_schema, ensure_ascii=False),
            description=description[:100] if description else None,
            icon=None,
            creator=creator
        )
        
        return tool
    
    @staticmethod
    async def test_tool(
        schema: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        测试工具（在保存前测试 API 调用）
        
        Args:
            schema: 工具的 OpenAPI Schema
            parameters: 测试参数
            
        Returns:
            测试结果，包含：
            - success: 是否成功
            - status_code: HTTP 状态码
            - response: 响应内容
            - error: 错误信息（如果有）
        """
        try:
            actual_schema = schema

            if not (schema.get("servers") and schema.get("paths")):
                inner_schema = schema.get("schema")
                if isinstance(inner_schema, dict) and (
                    inner_schema.get("servers") and inner_schema.get("paths")
                ):
                    actual_schema = inner_schema
                    logger.debug("从内层 schema.schema 中提取 OpenAPI Schema")

            servers = actual_schema.get("servers", [])
            if not servers:
                raise BusinessException("Schema 中未定义 servers")
            
            base_url = servers[0].get("url", "")
            if not base_url:
                raise BusinessException("服务器 URL 未定义")

            paths = actual_schema.get("paths", {})
            if not paths:
                raise BusinessException("Schema 中未定义 paths")
            
            path = list(paths.keys())[0]
            path_item = paths[path]

            method = None
            operation = None
            for m in ["get", "post", "put", "delete", "patch"]:
                if m in path_item:
                    method = m
                    operation = path_item[m]
                    break
            
            if not method or not operation:
                raise BusinessException("未找到有效的 HTTP 方法")

            url = base_url.rstrip("/") + path
            if parameters:
                for key, value in parameters.items():
                    url = url.replace(f"{{{key}}}", str(value))

            headers = {}
            query_params = {}
            body = None
            
            if parameters:
                param_locations = {}
                param_defs = operation.get("parameters", [])
                for param_def in param_defs:
                    param_name = param_def.get("name")
                    param_in = param_def.get("in", "query")
                    param_locations[param_name] = param_in

                for param_name, param_value in parameters.items():
                    param_in = param_locations.get(param_name)

                    if param_in is None:

                        if param_name.startswith(("X-", "Authorization", "Content-Type", "Accept")):
                            param_in = "header"
                    
                    if param_in == "query":
                        query_params[param_name] = param_value
                    elif param_in == "header":
                        headers[param_name] = param_value
                    elif param_in == "path":
                        pass

                request_body = operation.get("requestBody")
                if request_body:
                    content = request_body.get("content", {})
                    if "application/json" in content:
                        schema = content["application/json"].get("schema", {})
                        properties = schema.get("properties", {})
                        
                        if properties:
                            body_data = {}
                            for field_name in properties.keys():
                                if field_name in parameters:
                                    body_data[field_name] = parameters[field_name]

                            if not body_data:

                                body_params = {}
                                for param_name, param_value in parameters.items():
                                    param_in = param_locations.get(param_name)
                                    if param_in not in ["query", "header", "path"]:
                                        body_params[param_name] = param_value
                                body_data = body_params if body_params else None
                            
                            if body_data:
                                body = body_data
                                headers["Content-Type"] = "application/json"
                        else:
                            body_params = {}
                            for param_name, param_value in parameters.items():
                                param_in = param_locations.get(param_name)
                                if param_in not in ["query", "header", "path"]:
                                    body_params[param_name] = param_value
                            
                            if body_params:
                                body = body_params
                                headers["Content-Type"] = "application/json"
                    elif "application/x-www-form-urlencoded" in content:

                        body_params = {}
                        for param_name, param_value in parameters.items():
                            param_in = param_locations.get(param_name)
                            if param_in not in ["query", "header", "path"]:
                                body_params[param_name] = param_value
                        if body_params:
                            body = body_params
                            headers["Content-Type"] = "application/x-www-form-urlencoded"
                else:

                    if method.lower() in ["post", "put", "patch"]:
                        body_params = {}
                        for param_name, param_value in parameters.items():
                            param_in = param_locations.get(param_name)
                            if param_in not in ["query", "header", "path"]:
                                body_params[param_name] = param_value
                        
                        if body_params:
                            body = body_params
                            headers["Content-Type"] = "application/json"

                if "requestBody" in parameters and not body:
                    body = parameters["requestBody"]
                    headers["Content-Type"] = "application/json"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    params=query_params,
                    headers=headers,
                    json=body if body else None
                )

                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                
                return {
                    "success": response.is_success,
                    "status_code": response.status_code,
                    "response": response_data,
                    "error": None if response.is_success else f"HTTP {response.status_code}"
                }
        
        except httpx.TimeoutException:
            return {
                "success": False,
                "status_code": None,
                "response": None,
                "error": "请求超时"
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "status_code": None,
                "response": None,
                "error": f"请求失败: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "response": None,
                "error": str(e)
            }
    
    @staticmethod
    def batch_save_tools(
        db: Session,
        tools: List[Dict[str, Any]],
        category_name: Optional[str] = None,
        category_description: Optional[str] = None,
        category_icon: Optional[str] = None,
        creator: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        批量保存已解析的工具到数据库
        
        Args:
            db: 数据库会话
            tools: 工具列表，每个包含 name, schema, description
            category_name: 分类名称（如果提供）
            category_description: 分类描述
            category_icon: 分类图标
            creator: 创建人
            
        Returns:
            保存结果，包含：
            - category_id: 分类ID（如果创建了分类）
            - category_name: 分类名称
            - tools: 创建的工具列表
            - total_tools: 创建的工具总数
            - errors: 错误列表
        """
        errors = []
        created_tools = []
        category_id = None
        
        try:
            if category_name:
                if len(category_name) > 30:
                    raise BusinessException("分类名称长度不能超过30个字符")
                if category_description and len(category_description) > 100:
                    raise BusinessException("分类描述长度不能超过100个字符")

                from app.models.tool_category import ToolCategory
                existing_category = db.query(ToolCategory).filter(
                    ToolCategory.name == category_name
                ).first()
                if existing_category:
                    raise BusinessException(f'分类名称已存在: {category_name}')

            for tool_data in tools:
                try:
                    tool = ToolService.create_tool(
                        db=db,
                        name=tool_data.get("name", "未命名工具")[:30],
                        schema=json.dumps(tool_data.get("schema", {}), ensure_ascii=False),
                        description=tool_data.get("description", "")[:100] if tool_data.get("description") else None,
                        icon=tool_data.get("icon"),
                        creator=creator
                    )
                    
                    created_tools.append({
                        "id": tool.id,
                        "name": tool.name,
                        "method": tool_data.get("method", ""),
                        "path": tool_data.get("path", "")
                    })
                    
                    logger.info(f"保存工具成功: {tool.name}")
                except Exception as e:
                    error_msg = f"保存工具失败 ({tool_data.get('name', '未知')}): {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            if category_name and created_tools:
                try:
                    tool_ids = [tool["id"] for tool in created_tools]

                    logger.info(f"创建新分类: {category_name}")
                    category = ToolCategoryService.create_category(
                        db=db,
                        name=category_name,
                        description=category_description or f"包含 {len(tool_ids)} 个工具",
                        icon=category_icon,
                        sort_order=0,
                        creator=creator,
                        tool_ids=tool_ids
                    )
                    category_id = category.id

                    logger.info(f"工具已关联到分类: {category_name} (ID: {category_id})")
                except Exception as e:
                    error_msg = f"创建/更新分类失败: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            return {
                "category_id": category_id,
                "category_name": category_name,
                "tools": created_tools,
                "total_tools": len(created_tools),
                "errors": errors
            }
        
        except Exception as e:
            logger.error(f"批量保存工具失败: {str(e)}")
            raise BusinessException(f"批量保存工具失败: {str(e)}")
    
    @staticmethod
    def import_tools_from_schema(
        db: Session,
        schema: Dict[str, Any],
        category_name: Optional[str] = None,
        category_description: Optional[str] = None,
        category_icon: Optional[str] = None,
        auto_split: bool = True,
        creator: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        从 OpenAPI Schema 导入工具
        
        Args:
            db: 数据库会话
            schema: 完整的 OpenAPI Schema
            category_name: 分类名称（如果提供）
            category_description: 分类描述
            category_icon: 分类图标
            auto_split: 是否自动拆分成多个工具
            creator: 创建人
            
        Returns:
            导入结果，包含：
            - category_id: 分类ID（如果创建了分类）
            - category_name: 分类名称
            - tools: 创建的工具列表
            - total_tools: 创建的工具总数
            - errors: 错误列表
        """
        errors = []
        created_tools = []
        category_id = None
        
        try:

            if category_name:
                if len(category_name) > 30:
                    raise BusinessException("分类名称长度不能超过30个字符")
                if category_description and len(category_description) > 100:
                    raise BusinessException("分类描述长度不能超过100个字符")


            operations = ToolImportService.extract_operations_from_schema(schema)
            logger.info(f"从 Schema 中提取了 {len(operations)} 个操作")

            if not auto_split:

                tool_name = schema.get("info", {}).get("title", "导入的工具")[:30]
                tool_description = schema.get("info", {}).get("description", "")[:100]
                
                tool = ToolService.create_tool(
                    db=db,
                    name=tool_name,
                    schema=json.dumps(schema, ensure_ascii=False),
                    description=tool_description,
                    icon=None,
                    creator=creator
                )
                
                created_tools.append({
                    "id": tool.id,
                    "name": tool.name,
                    "operation_count": len(operations)
                })
                
                logger.info(f"创建了单个工具: {tool.name} (包含 {len(operations)} 个操作)")
            else:

                for op in operations:
                    try:
                        tool = ToolImportService.create_tool_from_operation(
                            db=db,
                            base_schema=schema,
                            path=op["path"],
                            method=op["method"],
                            operation=op["operation"],
                            operation_id=op["operation_id"],
                            summary=op["summary"],
                            description=op["description"],
                            creator=creator
                        )
                        
                        created_tools.append({
                            "id": tool.id,
                            "name": tool.name,
                            "operation_id": op["operation_id"],
                            "method": op["method"].upper(),
                            "path": op["path"]
                        })
                        
                        logger.info(f"创建工具成功: {tool.name} ({op['method'].upper()} {op['path']})")
                    except Exception as e:
                        error_msg = f"创建工具失败 ({op['method'].upper()} {op['path']}): {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
            

            if category_name and created_tools:
                try:

                    from app.models.tool_category import ToolCategory
                    existing_category = db.query(ToolCategory).filter(
                        ToolCategory.name == category_name
                    ).first()
                    
                    tool_ids = [tool["id"] for tool in created_tools]
                    
                    if existing_category:

                        logger.info(f"使用现有分类: {category_name}")

                        existing_tool_ids = [t.id for t in existing_category.tools.all()]
                        all_tool_ids = list(set(existing_tool_ids + tool_ids))

                        category = ToolCategoryService.update_category(
                            db=db,
                            category_id=existing_category.id,
                            tool_ids=all_tool_ids
                        )
                        category_id = category.id
                    else:

                        logger.info(f"创建新分类: {category_name}")
                        category = ToolCategoryService.create_category(
                            db=db,
                            name=category_name,
                            description=category_description or f"包含 {len(tool_ids)} 个工具",
                            icon=category_icon,
                            sort_order=0,
                            creator=creator,
                            tool_ids=tool_ids
                        )
                        category_id = category.id
                    
                    logger.info(f"工具已关联到分类: {category_name} (ID: {category_id})")
                except Exception as e:
                    error_msg = f"创建/更新分类失败: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            return {
                "category_id": category_id,
                "category_name": category_name,
                "tools": created_tools,
                "total_tools": len(created_tools),
                "errors": errors
            }
        
        except InvalidSchemaException as e:
            raise e
        except Exception as e:
            logger.error(f"导入工具失败: {str(e)}")
            raise BusinessException(f"导入工具失败: {str(e)}")

