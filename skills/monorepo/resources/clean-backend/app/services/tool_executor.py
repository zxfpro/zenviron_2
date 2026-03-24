"""
工具执行引擎（FastAPI 版本）
"""
import requests
import json
import logging
from sqlalchemy.orm import Session
from app.config import settings
from app.services.tool_service import ToolService
from app.utils.exceptions import (
    ToolExecutionException,
    ToolDisabledException,
    ToolNotFoundException,
    InvalidSchemaException,
    CategoryDisabledException
)

logger = logging.getLogger(__name__)


class ToolExecutor:
    """工具执行器"""
    
    @staticmethod
    def execute(db: Session, tool_id, parameters=None):
        """
        执行工具
        
        Args:
            db: 数据库会话
            tool_id: 工具ID
            parameters: 工具参数
            
        Returns:
            执行结果
            
        Raises:
            ToolNotFoundException: 工具不存在
            ToolDisabledException: 工具已停用
            CategoryDisabledException: 工具所属分类已停用
            ToolExecutionException: 工具执行失败
        """
        if parameters is None:
            parameters = {}

        tool = ToolService.get_tool_by_id(db, tool_id)

        if not tool.is_enabled():
            raise ToolDisabledException(tool.name)

        categories = tool.categories.all()
        if categories:
            disabled_categories = [cat for cat in categories if not cat.is_enabled()]
            if disabled_categories:

                raise CategoryDisabledException(disabled_categories[0].name)

        try:
            result = ToolExecutor._execute_from_schema(tool.schema, parameters)
            return result
        except Exception as e:
            logger.error(f'Tool execution failed [{tool.name}]: {str(e)}', exc_info=True)
            raise ToolExecutionException(tool.name, str(e))
    
    @staticmethod
    def _execute_from_schema(schema, parameters):
        """
        根据Schema执行HTTP请求
        
        Args:
            schema: OpenAPI/Swagger格式的Schema
            parameters: 请求参数
            
        Returns:
            执行结果
        """

        base_url = ToolExecutor._extract_base_url(schema)

        path, method, operation = ToolExecutor._extract_operation(schema)

        url = f"{base_url}{path}"

        ToolExecutor._validate_parameters(operation, parameters)

        headers = ToolExecutor._build_headers(schema, operation, parameters)

        request_params = ToolExecutor._build_request_params(method, operation, parameters)

        logger.info(f'执行工具请求: {method.upper()} {url}')
        logger.debug(f'请求头: {headers}')
        logger.debug(f'请求参数: {request_params}')

        timeout = settings.TOOL_REQUEST_TIMEOUT
        max_retries = settings.TOOL_MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    timeout=timeout,
                    **request_params
                )

                return ToolExecutor._handle_response(response)
                
            except requests.Timeout:
                if attempt == max_retries - 1:
                    raise Exception(f'请求超时，已重试{max_retries}次')
                logger.warning(f'Request timeout, retrying... (attempt {attempt + 1}/{max_retries})')
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f'请求失败: {str(e)}')
                logger.warning(f'Request failed, retrying... (attempt {attempt + 1}/{max_retries}): {str(e)}')
    
    @staticmethod
    def _extract_base_url(schema):
        """提取基础URL"""

        if 'servers' in schema and schema['servers']:
            return schema['servers'][0]['url']

        if 'host' in schema:
            scheme = schema.get('schemes', ['https'])[0]
            base_path = schema.get('basePath', '')
            return f"{scheme}://{schema['host']}{base_path}"
        
        raise InvalidSchemaException('无法从Schema中提取基础URL')
    
    @staticmethod
    def _extract_operation(schema):
        """提取API操作信息"""
        paths = schema.get('paths', {})
        if not paths:
            raise InvalidSchemaException('Schema中没有定义任何API路径')

        path = list(paths.keys())[0]
        path_item = paths[path]

        methods = ['get', 'post', 'put', 'delete', 'patch']
        for method in methods:
            if method in path_item:
                return path, method, path_item[method]
        
        raise InvalidSchemaException(f'路径 {path} 没有定义任何HTTP方法')
    
    @staticmethod
    def _build_headers(schema, operation, parameters):
        """
        构建请求头
        
        Args:
            schema: OpenAPI Schema
            operation: 操作定义
            parameters: 用户传入的参数字典
            
        Returns:
            请求头字典
        """
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'ToolServer/1.0'
        }

        op_parameters = operation.get('parameters', [])
        for param in op_parameters:
            if param.get('in') == 'header':
                param_name = param.get('name')

                if param_name in parameters:
                    headers[param_name] = str(parameters[param_name])
        
        return headers
    
    @staticmethod
    def _validate_parameters(operation, parameters):
        """
        验证参数
        
        检查所有必填参数（包括query、header、body等）
        同时检查是否有重复的参数名
        支持 OpenAPI 3.0 的 requestBody
        """
        op_parameters = operation.get('parameters', [])

        param_names = {}
        for param in op_parameters:
            param_name = param.get('name')
            param_in = param.get('in', 'query')
            
            if param_name in param_names:
                existing_location = param_names[param_name]
                if existing_location != param_in:
                    logger.warning(
                        f'⚠️  发现重复参数名 "{param_name}" 在不同位置: '
                        f'{existing_location} 和 {param_in}。'
                        f'这是不推荐的做法，可能导致参数处理混乱！'
                    )
                    raise InvalidSchemaException(
                        f'参数名重复: "{param_name}" 在 {existing_location} 和 {param_in} 中都有定义。'
                        f'请使用不同的参数名以避免混淆。'
                    )
            param_names[param_name] = param_in

        for param in op_parameters:
            if param.get('required', False):
                param_name = param.get('name')
                param_in = param.get('in', 'query')
                if param_name not in parameters:
                    raise InvalidSchemaException(f'缺少必填参数: {param_name} (位置: {param_in})')

        request_body = operation.get('requestBody')
        if request_body and request_body.get('required', False):
            content = request_body.get('content', {})
            if content and not parameters:
                pass
    
    @staticmethod
    def _build_request_params(method, operation, parameters):
        """
        构建请求参数（排除Header参数）
        
        支持 OpenAPI 3.0 的 requestBody 和 parameters
        
        Args:
            method: HTTP方法
            operation: 操作定义
            parameters: 用户传入的参数字典
            
        Returns:
            请求参数字典（用于requests库）
        """
        request_params = {}

        query_params = {}
        body_data = None
        
        op_parameters = operation.get('parameters', [])
        request_body = operation.get('requestBody')

        param_locations = {}
        for param in op_parameters:
            param_name = param.get('name')
            param_in = param.get('in', 'query')
            if param_name not in param_locations:
                param_locations[param_name] = param_in

        if request_body:
            content = request_body.get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                properties = schema.get('properties', {})
                required_fields = schema.get('required', [])

                if properties:

                    body_data = {}
                    for field_name in properties.keys():
                        if field_name in parameters:
                            body_data[field_name] = parameters[field_name]

                    if not body_data:

                        body_params = {}
                        for param_name, param_value in parameters.items():
                            param_in = param_locations.get(param_name)
                            if param_in not in ['query', 'header']:
                                body_params[param_name] = param_value
                        body_data = body_params if body_params else None
                else:

                    body_params = {}
                    for param_name, param_value in parameters.items():
                        param_in = param_locations.get(param_name)
                        if param_in not in ['query', 'header']:
                            body_params[param_name] = param_value
                    body_data = body_params if body_params else None
                    
                logger.debug(f'构建 requestBody: {body_data}')
            elif 'application/x-www-form-urlencoded' in content:

                body_data = {k: v for k, v in parameters.items() if param_locations.get(k) not in ['query', 'header']}

        for param_name, param_value in parameters.items():
            param_in = param_locations.get(param_name, 'query')
            if param_in == 'query':
                query_params[param_name] = param_value

        if body_data is None:
            body_params = {}
            for param_name, param_value in parameters.items():
                param_in = param_locations.get(param_name, 'query')
                if param_in == 'body' or param_in == 'formData':
                    body_params[param_name] = param_value
            
            if method.lower() in ['get', 'delete']:

                request_params['params'] = query_params
            else:
                if body_params:
                    request_params['json'] = body_params
                if query_params:
                    request_params['params'] = query_params
        else:
            if method.lower() in ['get', 'delete']:
                request_params['params'] = query_params
            else:
                if body_data:
                    request_params['json'] = body_data
                if query_params:
                    request_params['params'] = query_params
        
        return request_params
    
    @staticmethod
    def _handle_response(response):
        """处理响应"""

        if response.status_code >= 400:
            raise Exception(f'HTTP错误: {response.status_code}, {response.text}')

        try:
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.json()
            }
        except json.JSONDecodeError:

            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.text
            }
    
    @staticmethod
    def test_tool(db: Session, tool_id, parameters=None):
        """
        测试工具
        
        Args:
            db: 数据库会话
            tool_id: 工具ID
            parameters: 测试参数
            
        Returns:
            测试结果
        """
        if parameters is None:
            parameters = {}

        tool = ToolService.get_tool_by_id(db, tool_id)

        try:
            result = ToolExecutor._execute_from_schema(tool.schema, parameters)
            return {
                'success': True,
                'result': result
            }
        except Exception as e:
            logger.error(f'Tool test failed [{tool.name}]: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

