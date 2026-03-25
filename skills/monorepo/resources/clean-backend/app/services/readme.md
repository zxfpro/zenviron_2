这里具体存放 结构业务逻辑的实现
具体参考如下

```python

import json
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.tool import Tool
from app.utils.exceptions import (
    ToolNotFoundException,
    ToolNameDuplicateException,
    InvalidSchemaException
)


class ToolService:
    """工具管理服务"""
    
    @staticmethod
    def create_tool(db: Session, name, schema, description=None, icon=None, creator=None):
        """
        创建工具
        
        Args:
            db: 数据库会话
            name: 工具名称
            schema: 工具Schema配置（JSON字符串）
            description: 工具描述
            icon: 工具图标
            creator: 创建人
            
        Returns:
            创建的工具对象
            
        Raises:
            InvalidSchemaException: Schema格式无效
        """
        try:
            schema_dict = json.loads(schema)
        except json.JSONDecodeError as e:
            raise InvalidSchemaException(f'JSON解析失败: {str(e)}')

        ToolService._validate_schema(schema_dict)

        tool = Tool(
            name=name,
            description=description,
            schema=schema_dict,
            icon=icon,
            creator=creator,
            status='enabled'
        )
        
        db.add(tool)
        db.commit()
        db.refresh(tool)
        
        return tool

    @staticmethod
    def get_tool_by_id(db: Session, tool_id):
        """
        根据ID获取工具

        Args:
            db: 数据库会话
            tool_id: 工具ID

        Returns:
            工具对象

        Raises:
            ToolNotFoundException: 工具不存在
        """
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        # if not tool:
        #     raise ToolNotFoundException(tool_id)
        return tool

    @staticmethod
    def get_tools_by_ids(db: Session, tool_ids):
        """
        根据ID列表获取多个工具

        Args:
            db: 数据库会话
            tool_ids: 工具ID列表

        Returns:
            工具对象列表（按ID顺序返回）
        """
        tools = db.query(Tool).filter(Tool.id.in_(tool_ids)).all()

        tools_dict = {tool.id: tool for tool in tools}
        return [tools_dict[tid] for tid in tool_ids if tid in tools_dict]

    @staticmethod
    def get_tool_by_name(db: Session, name):
        """
        根据名称获取工具
        
        Args:
            db: 数据库会话
            name: 工具名称
            
        Returns:
            工具对象，不存在返回None
        """
        return db.query(Tool).filter(Tool.name == name).first()
    
    @staticmethod
    def update_tool(db: Session, tool_id, **kwargs):
        """
        更新工具
        
        Args:
            db: 数据库会话
            tool_id: 工具ID
            **kwargs: 更新的字段
            
        Returns:
            更新后的工具对象
            
        Raises:
            ToolNotFoundException: 工具不存在
            InvalidSchemaException: Schema格式无效
        """
        tool = ToolService.get_tool_by_id(db, tool_id)

        if 'schema' in kwargs:
            try:
                schema_dict = json.loads(kwargs['schema'])
                ToolService._validate_schema(schema_dict)
                kwargs['schema'] = schema_dict
            except json.JSONDecodeError as e:
                raise InvalidSchemaException(f'JSON解析失败: {str(e)}')

        for key, value in kwargs.items():
            if hasattr(tool, key):
                setattr(tool, key, value)
        
        db.commit()
        db.refresh(tool)
        return tool
    
    @staticmethod
    def delete_tool(db: Session, tool_id):
        """
        删除工具

        Args:
            db: 数据库会话
            tool_id: 工具ID
            
        Raises:
            ToolNotFoundException: 工具不存在
        """
        tool = ToolService.get_tool_by_id(db, tool_id)
        db.delete(tool)
        db.commit()
    
    @staticmethod
    def _validate_schema(schema_dict):
        """
        验证 Schema 格式
        
        检查参数定义是否合理，特别是检查是否有重复的参数名
        
        Args:
            schema_dict: 解析后的 Schema 字典
            
        Raises:
            InvalidSchemaException: Schema 格式无效
        """
        if 'paths' not in schema_dict:
            raise InvalidSchemaException('Schema 必须包含 paths 定义')
        
        paths = schema_dict.get('paths', {})
        for path, path_item in paths.items():
            for method in ['get', 'post', 'put', 'delete', 'patch']:
                if method not in path_item:
                    continue
                
                operation = path_item[method]
                parameters = operation.get('parameters', [])

                param_defs = {}
                for param in parameters:
                    param_name = param.get('name')
                    param_in = param.get('in', 'query')
                    
                    if param_name not in param_defs:
                        param_defs[param_name] = []
                    param_defs[param_name].append(param_in)

                for param_name, locations in param_defs.items():
                    if len(locations) > 1:
                        unique_locations = list(set(locations))
                        if len(unique_locations) > 1:
                            raise InvalidSchemaException(
                                f'参数名 "{param_name}" 在多个位置重复定义: {", ".join(unique_locations)}。'
                                f'同一个参数不应该在不同位置（header、query、body等）使用相同的名称，'
                                f'这会导致参数处理混乱。请使用不同的参数名。'
                            )
    
    @staticmethod
    def enable_tool(db: Session, tool_id):
        """
        启用工具
        
        Args:
            db: 数据库会话
            tool_id: 工具ID
            
        Returns:
            更新后的工具对象
            
        Raises:
            ToolNotFoundException: 工具不存在
        """
        tool = ToolService.get_tool_by_id(db, tool_id)
        tool.enable()
        db.commit()
        db.refresh(tool)
        return tool
    
    @staticmethod
    def disable_tool(db: Session, tool_id):
        """
        停用工具
        
        Args:
            db: 数据库会话
            tool_id: 工具ID
            
        Returns:
            更新后的工具对象
            
        Raises:
            ToolNotFoundException: 工具不存在
        """
        tool = ToolService.get_tool_by_id(db, tool_id)
        tool.disable()
        db.commit()
        db.refresh(tool)
        return tool
    
    @staticmethod
    def list_tools(db: Session, keyword=None, status=None, page=1, page_size=10):
        """
        查询工具列表
        
        Args:
            db: 数据库会话
            keyword: 关键字（支持ID或名称模糊查询）
            status: 状态筛选（enabled/disabled/all）
            page: 页码
            page_size: 每页大小
            
        Returns:
            (工具列表, 总数量)
        """
        query = db.query(Tool)

        if keyword:
            try:
                tool_id = int(keyword)
                query = query.filter(
                    or_(
                        Tool.id == tool_id,
                        Tool.name.like(f'%{keyword}%')
                    )
                )
            except ValueError:
                query = query.filter(Tool.name.like(f'%{keyword}%'))

        if status and status != 'all':
            query = query.filter(Tool.status == status)

        query = query.order_by(Tool.updated_at.desc())

        total = query.count()
        tools = query.limit(page_size).offset((page - 1) * page_size).all()
        
        return tools, total



```