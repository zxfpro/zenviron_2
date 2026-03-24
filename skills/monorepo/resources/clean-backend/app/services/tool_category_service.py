"""
工具分类管理服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Tuple, Dict, Any, Set
from app.models.tool_category import ToolCategory
from app.models.tool import Tool
from app.utils.exceptions import (
    BusinessException,
    InvalidSchemaException
)
import json
import logging

logger = logging.getLogger(__name__)


def _normalize_schema_to_dict(schema_value: Any) -> Dict[str, Any]:
    """
    规范化 schema 为 dict。

    SQLAlchemy JSON 字段在不同写入路径下可能出现 dict / str / None。
    为了统一后续处理（合并、提取 paths、对外返回），这里统一转换为 dict。
    """
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


class ToolCategoryService:
    """工具分类管理服务"""

    @staticmethod
    def create_category(
            db: Session,
            name: str,
            description: str = None,
            icon: str = None,
            sort_order: int = 0,
            creator: str = None,
            tool_ids: List[int] = None
    ) -> ToolCategory:
        """
        创建工具分类

        Args:
            db: 数据库会话
            name: 分类名称
            description: 分类描述
            icon: 分类图标
            sort_order: 排序顺序
            creator: 创建人
            tool_ids: 关联的工具ID列表

        Returns:
            创建的分类对象

        Raises:
            BusinessException: 分类名称已存在或工具ID不存在
        """
        if len(name) > 30:
            raise BusinessException('分类名称长度不能超过30个字符')
        if description and len(description) > 100:
            raise BusinessException('分类描述长度不能超过100个字符')

        existing = db.query(ToolCategory).filter(ToolCategory.name == name).first()
        if existing:
            raise BusinessException(f'分类名称 "{name}" 已存在')

        category = ToolCategory(
            name=name,
            description=description,
            icon=icon,
            sort_order=sort_order,
            creator=creator,
            status='enabled'
        )

        db.add(category)
        db.flush()

        if tool_ids:
            tools = db.query(Tool).filter(Tool.id.in_(tool_ids)).all()
            found_ids = {tool.id for tool in tools}
            missing_ids = set(tool_ids) - found_ids

            if missing_ids:
                raise BusinessException(f'工具ID不存在: {", ".join(map(str, missing_ids))}')

            for tool in tools:
                category.tools.append(tool)

        db.commit()
        db.refresh(category)

        return category

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> ToolCategory:
        """
        根据ID获取分类

        Args:
            db: 数据库会话
            category_id: 分类ID

        Returns:
            分类对象

        Raises:
            BusinessException: 分类不存在
        """
        category = db.query(ToolCategory).filter(ToolCategory.id == category_id).first()
        if not category:
            raise BusinessException(f'分类不存在: {category_id}', 404)
        return category

    @staticmethod
    def list_categories(
            db: Session,
            keyword: str = None,
            status: str = 'all',
            page: int = 1,
            page_size: int = 20
    ) -> Tuple[List[ToolCategory], int]:
        """
        获取分类列表

        Args:
            db: 数据库会话
            keyword: 关键字搜索
            status: 状态筛选 (all/enabled/disabled)
            page: 页码
            page_size: 每页大小

        Returns:
            (分类列表, 总数)
        """
        query = db.query(ToolCategory)

        if keyword:
            try:
                keyword_id = int(keyword)
                query = query.filter(
                    or_(
                        ToolCategory.id == keyword_id,
                        ToolCategory.name.like(f'%{keyword}%')
                    )
                )
            except ValueError:
                query = query.filter(ToolCategory.name.like(f'%{keyword}%'))

        if status and status != 'all':
            query = query.filter(ToolCategory.status == status)

        query = query.order_by(ToolCategory.sort_order.asc(), ToolCategory.created_at.desc())

        total = query.count()

        categories = query.offset((page - 1) * page_size).limit(page_size).all()

        return categories, total

    @staticmethod
    def update_category(db: Session, category_id: int, **kwargs) -> ToolCategory:
        """
        更新分类

        Args:
            db: 数据库会话
            category_id: 分类ID
            **kwargs: 更新的字段（name, description, schema）

        Returns:
            更新后的分类对象

        Raises:
            BusinessException: 分类不存在或名称重复
        """
        category = ToolCategoryService.get_category_by_id(db, category_id)

        if 'name' in kwargs and kwargs['name'] and len(kwargs['name']) > 30:
            raise BusinessException('分类名称长度不能超过30个字符')
        if 'description' in kwargs and kwargs['description'] and len(kwargs['description']) > 100:
            raise BusinessException('分类描述长度不能超过100个字符')

        if 'name' in kwargs and kwargs['name'] != category.name:
            existing = db.query(ToolCategory).filter(
                ToolCategory.name == kwargs['name'],
                ToolCategory.id != category_id
            ).first()
            if existing:
                raise BusinessException(f'分类名称 "{kwargs["name"]}" 已存在')

        schema = kwargs.pop('schema', None)
        if schema is not None:
            if not isinstance(schema, dict):
                raise BusinessException('schema 必须是一个对象')

            if 'paths' not in schema or not isinstance(schema['paths'], dict):
                raise BusinessException('schema 缺少 paths 字段或 paths 不是对象')

            # 根据 schema 中的 paths 智能合并工具
            ToolCategoryService._smart_merge_tools_by_schema(db, category, schema)

        # 更新其他字段（name, description）
        for key, value in kwargs.items():
            if hasattr(category, key) and value is not None:
                setattr(category, key, value)

        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int, delete_tools: bool = True):
        """
        删除分类（可选择是否删除关联的工具）

        Args:
            db: 数据库会话
            category_id: 分类ID
            delete_tools: 是否删除关联的工具（默认True）
                - True: 删除仅属于该分类的工具（智能删除）
                - False: 只删除分类和关联关系，保留所有工具

        Returns:
            dict: 删除统计信息，包含 success 字段表示是否成功删除

        Note:
            智能删除模式：
            - 如果工具只属于这一个分类，则删除工具本身
            - 如果工具还属于其他分类，则只删除关联关系，保留工具
            - 如果分类下的工具被智能体使用，则不删除分类，返回失败信息
        """
        from sqlalchemy import  or_, and_
        from app.models.ai_agent import AiAgent

        category = ToolCategoryService.get_category_by_id(db, category_id)

        tool_ids = [tool.id for tool in category.tools.all()]

        if tool_ids:
            all_agents = db.query(AiAgent).filter(
                and_(
                    AiAgent.tools.isnot(None),
                    or_(AiAgent.del_flag == None, AiAgent.del_flag == '0')
                )
            ).all()

            agents_using_tools = []
            tool_ids_set = set(tool_ids)

            for agent in all_agents:
                try:
                    tools_data = agent.tools
                    if isinstance(tools_data, str):
                        tools_data = json.loads(tools_data)

                    if not isinstance(tools_data, dict):
                        continue

                    ai_tool_type_list = tools_data.get('aiToolTypeList', [])
                    for tool_type_item in ai_tool_type_list:
                        if not isinstance(tool_type_item, dict):
                            continue
                        ai_tool_list = tool_type_item.get('aiToolList', [])
                        for tool_item in ai_tool_list:
                            if not isinstance(tool_item, dict):
                                continue
                            tool_id = tool_item.get('toolId')
                            if tool_id and tool_id in tool_ids_set:
                                agents_using_tools.append(agent)
                                break
                        if agent in agents_using_tools:
                            break
                except (json.JSONDecodeError, TypeError, AttributeError) as e:
                    logger.warning(f"解析智能体 {agent.id} 的 tools 字段失败: {str(e)}")
                    continue

            if agents_using_tools:
                agent_names = [agent.name or f"智能体#{agent.id}" for agent in agents_using_tools]
                agent_names_str = "、".join(agent_names[:5])
                if len(agent_names) > 5:
                    agent_names_str += f" 等{len(agent_names)}个"

                return {
                    'success': False,
                    'category_name': category.name,
                    'message': '该工具已被绑定，不允许删除'
                }

        stats = {
            'success': True,
            'category_name': category.name,
            'total_tools': category.tools.count(),
            'deleted_tools': 0,
            'kept_tools': 0
        }

        if delete_tools:
            tools_to_check = list(category.tools.all())

            for tool in tools_to_check:
                category_count = tool.categories.count()

                if category_count == 1:
                    db.delete(tool)
                    stats['deleted_tools'] += 1
                else:
                    stats['kept_tools'] += 1

        db.delete(category)
        db.commit()

        return stats

    @staticmethod
    def enable_category(db: Session, category_id: int) -> ToolCategory:
        """启用分类"""
        category = ToolCategoryService.get_category_by_id(db, category_id)
        category.enable()
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def disable_category(db: Session, category_id: int):
        """
        停用分类

        Args:
            db: 数据库会话
            category_id: 分类ID

        Returns:
            dict: 停用结果，包含 success 字段表示是否成功停用

        Note:
            如果分类下的工具被智能体使用，则不停用分类，返回失败信息
        """
        from sqlalchemy import func, or_, and_
        from app.models.ai_agent import AiAgent

        category = ToolCategoryService.get_category_by_id(db, category_id)

        tool_ids = [tool.id for tool in category.tools.all()]

        if tool_ids:

            all_agents = db.query(AiAgent).filter(
                and_(
                    AiAgent.tools.isnot(None),
                    or_(AiAgent.del_flag == None, AiAgent.del_flag == '0')
                )
            ).all()

            agents_using_tools = []
            tool_ids_set = set(tool_ids)

            for agent in all_agents:
                try:

                    tools_data = agent.tools
                    if isinstance(tools_data, str):
                        tools_data = json.loads(tools_data)

                    if not isinstance(tools_data, dict):
                        continue


                    ai_tool_type_list = tools_data.get('aiToolTypeList', [])
                    for tool_type_item in ai_tool_type_list:
                        if not isinstance(tool_type_item, dict):
                            continue
                        ai_tool_list = tool_type_item.get('aiToolList', [])
                        for tool_item in ai_tool_list:
                            if not isinstance(tool_item, dict):
                                continue
                            tool_id = tool_item.get('toolId')
                            if tool_id and tool_id in tool_ids_set:
                                agents_using_tools.append(agent)
                                break
                        if agent in agents_using_tools:
                            break
                except (json.JSONDecodeError, TypeError, AttributeError) as e:
                    logger.warning(f"解析智能体 {agent.id} 的 tools 字段失败: {str(e)}")
                    continue

            if agents_using_tools:

                return {
                    'success': False,
                    'category_name': category.name,
                    'message': '该工具已被绑定，不允许停用'
                }

        category.disable()
        db.commit()
        db.refresh(category)

        return {
            'success': True,
            'category_name': category.name,
            'category_id': category.id,
            'status': category.status
        }

    @staticmethod
    def get_tools_in_category(
            db: Session,
            category_id: int,
            page: int = 1,
            page_size: int = 20
    ) -> Tuple[List[Tool], int]:
        """
        获取分类下的工具列表

        Args:
            db: 数据库会话
            category_id: 分类ID
            page: 页码
            page_size: 每页大小

        Returns:
            (工具列表, 总数)
        """
        category = ToolCategoryService.get_category_by_id(db, category_id)

        total = category.tools.count()

        tools = category.tools.offset((page - 1) * page_size).limit(page_size).all()

        return tools, total

    @staticmethod
    def _extract_tool_paths(tool: Tool) -> Set[str]:
        """
        从工具的 schema 中提取所有路径（path）

        Args:
            tool: 工具对象

        Returns:
            路径集合，格式："/api/path" 或 "/api/path:METHOD"
        """
        paths = set()
        try:
            schema = tool.schema
            if isinstance(schema, str):
                schema = json.loads(schema)

            if not isinstance(schema, dict):
                return paths

            schema_paths = schema.get('paths', {})
            for path, path_item in schema_paths.items():
                if isinstance(path_item, dict):

                    methods = [m for m in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options'] if
                               m in path_item]
                    if methods:
                        for method in methods:
                            paths.add(f"{path}:{method.upper()}")
                    else:
                        paths.add(path)
                else:
                    paths.add(path)

        except Exception as e:
            logger.warning(f"提取工具 {tool.id} 的路径失败: {str(e)}")

        return paths

    @staticmethod
    def _build_tool_path_map(tools: List[Tool]) -> Dict[str, Tool]:
        """
        构建工具路径到工具对象的映射

        Args:
            tools: 工具列表

        Returns:
            路径到工具的映射字典
        """
        path_map = {}
        for tool in tools:
            paths = ToolCategoryService._extract_tool_paths(tool)
            for path in paths:
                path_map[path] = tool
        return path_map

    @staticmethod
    def _smart_merge_tools_by_path(
            db: Session,
            category: ToolCategory,
            tools: List[Dict[str, Any]]
    ):
        """
        通过路径智能合并工具关联关系

        Args:
            db: 数据库会话
            category: 分类对象
            tools: 工具列表，每个包含 path、method、tool_id 或 schema

        规则：
        1. 提取新传入的 tools 列表中的所有 path
        2. 获取分类下现有工具的所有 path
        3. 对比差异：
           - 新列表中有但现有列表中没有：添加关联（创建新工具或关联现有工具）
           - 现有列表中有但新列表中没有：取消关联
           - 两边都有：保持关联
        """
        from app.services.tool_service import ToolService

        existing_tools = list(category.tools.all())
        existing_path_map = ToolCategoryService._build_tool_path_map(existing_tools)

        new_paths = set()
        new_tool_map = {}

        for tool_info in tools:
            path = tool_info.get('path')
            method = tool_info.get('method', '').upper()

            if not path:
                logger.warning("工具信息缺少 path 字段，跳过")
                continue

            path_key = f"{path}:{method}" if method else path
            new_paths.add(path_key)
            new_tool_map[path_key] = tool_info

        paths_to_remove = set(existing_path_map.keys()) - new_paths

        paths_to_add = new_paths - set(existing_path_map.keys())

        tools_to_remove = set()
        for path_key in paths_to_remove:
            tool = existing_path_map.get(path_key)
            if tool:
                tools_to_remove.add(tool)
                logger.info(f"移除工具关联: {tool.name} (path: {path_key})")

        for tool in tools_to_remove:
            if tool in category.tools:
                category.tools.remove(tool)

        for path_key in paths_to_add:
            tool_info = new_tool_map[path_key]

            if 'tool_id' in tool_info and tool_info['tool_id']:
                tool = db.query(Tool).filter(Tool.id == tool_info['tool_id']).first()
                if tool:
                    if tool not in category.tools:
                        category.tools.append(tool)
                        logger.info(f"添加现有工具到分类: {tool.name} (path: {path_key})")
                else:
                    logger.warning(f"工具ID不存在: {tool_info['tool_id']} (path: {path_key})")
            elif 'schema' in tool_info and tool_info['schema']:
                try:
                    schema = tool_info['schema']
                    tool_name = schema.get('info', {}).get('title', f"tool_{path_key.replace('/', '_')}")[:30]
                    tool_description = schema.get('info', {}).get('description', '')[:100]

                    tool = ToolService.create_tool(
                        db=db,
                        name=tool_name,
                        schema=json.dumps(schema, ensure_ascii=False),
                        description=tool_description if tool_description else None,
                        icon=None,
                        creator=None
                    )

                    if tool not in category.tools:
                        category.tools.append(tool)
                        logger.info(f"创建新工具并添加到分类: {tool.name} (path: {path_key})")
                except Exception as e:
                    logger.error(f"创建工具失败 (path: {path_key}): {str(e)}")
            else:
                logger.warning(f"工具信息缺少 tool_id 或 schema (path: {path_key})")

        logger.info(f"智能合并完成: 添加 {len(paths_to_add)} 个工具，移除 {len(paths_to_remove)} 个工具")

    @staticmethod
    def _filter_schema_by_paths(
            schema: Dict[str, Any],
            paths_to_keep: Set[str]
    ) -> Dict[str, Any]:
        """
        过滤 schema，只保留指定的 paths

        Args:
            schema: 原始的 OpenAPI Schema
            paths_to_keep: 需要保留的路径集合，格式："/api/path:METHOD"

        Returns:
            过滤后的 Schema
        """
        import copy

        filtered_schema = copy.deepcopy(schema)

        original_paths = filtered_schema.get('paths', {})
        filtered_paths = {}

        for path, path_item in original_paths.items():
            if not isinstance(path_item, dict):

                if path in paths_to_keep:
                    filtered_paths[path] = path_item
                continue

            http_methods = ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']
            filtered_path_item = {}

            for method in http_methods:
                if method in path_item:
                    path_key = f"{path}:{method.upper()}"
                    if path_key in paths_to_keep:
                        filtered_path_item[method] = path_item[method]

            if filtered_path_item:
                filtered_paths[path] = filtered_path_item

        filtered_schema['paths'] = filtered_paths

        return filtered_schema

    @staticmethod
    def _smart_merge_tools_by_schema(
            db: Session,
            category: ToolCategory,
            schema: Dict[str, Any]
    ):
        """
        通过 OpenAPI Schema 中的 paths 智能合并工具关联关系

        Args:
            db: 数据库会话
            category: 分类对象
            schema: OpenAPI Schema（包含 paths）

        规则：
        1. 提取 schema 中的所有 paths（包含 method）
        2. 获取分类下现有工具的所有 paths
        3. 对比差异：
           - schema 中有但现有列表中没有：创建新工具并关联
           - 现有列表中有但 schema 中没有：取消关联
           - 两边都有：更新该工具的信息
        """
        from app.services.tool_import_service import ToolImportService

        new_paths = set()
        path_schema_map = {}

        schema_paths = schema.get('paths', {})
        for path, path_item in schema_paths.items():
            if isinstance(path_item, dict):
                http_methods = ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']
                for method in http_methods:
                    if method in path_item:
                        path_key = f"{path}:{method.upper()}"
                        new_paths.add(path_key)
                        path_schema_map[path_key] = (path, method, path_item[method])
            else:
                new_paths.add(path)
                path_schema_map[path] = (path, None, path_item)

        existing_tools = list(category.tools.all())
        existing_path_map = ToolCategoryService._build_tool_path_map(existing_tools)

        paths_to_remove = set(existing_path_map.keys()) - new_paths

        paths_to_add = new_paths - set(existing_path_map.keys())

        paths_to_update = new_paths & set(existing_path_map.keys())

        tools_to_remove = set()
        for path_key in paths_to_remove:
            tool = existing_path_map.get(path_key)
            if tool:
                tools_to_remove.add(tool)
                logger.info(f"标记移除工具关联: {tool.name} (path: {path_key})")

        for tool in tools_to_remove:
            if tool in category.tools:
                category.tools.remove(tool)

        for path_key in paths_to_update:
            tool = existing_path_map.get(path_key)
            if not tool:
                continue

            path, method, operation = path_schema_map.get(path_key)
            if not operation:
                continue

            try:
                tool_schema = {
                    "openapi": schema.get("openapi", "3.0.0"),
                    "info": {
                        "title": operation.get("summary", f"{method.upper() if method else ''} {path}"),
                        "version": schema.get("info", {}).get("version", "1.0.0"),
                        "description": operation.get("description", "")
                    },
                    "servers": schema.get("servers", []),
                    "paths": {
                        path: {
                            method: operation
                        } if method else operation
                    }
                }

                if "components" in schema:
                    tool_schema["components"] = schema["components"]

                if operation.get("summary"):
                    tool_name = operation.get("summary")[:30]
                else:
                    from app.services.tool_import_service import ToolImportService
                    tool_name = ToolImportService._generate_tool_name_from_path(path, method or 'get')

                tool_description = operation.get("description", "")[:100] if operation.get("description") else None

                tool.name = tool_name
                tool.description = tool_description

                from app.services.tool_service import ToolService
                ToolService._validate_schema(tool_schema)
                tool.schema = tool_schema

                logger.info(f"更新工具: {tool.name} (path: {path_key})")
            except Exception as e:
                logger.error(f"更新工具失败 (path: {path_key}): {str(e)}")

        if paths_to_add:
            try:

                filtered_schema = ToolCategoryService._filter_schema_by_paths(
                    schema, paths_to_add
                )

                import_result = ToolImportService.import_tools_from_schema(
                    db=db,
                    schema=filtered_schema,
                    category_name=None,
                    auto_split=True,
                    creator=None
                )

                if import_result["tools"]:
                    new_tool_ids = [tool["id"] for tool in import_result["tools"]]

                    new_tools = db.query(Tool).filter(Tool.id.in_(new_tool_ids)).all()

                    for new_tool in new_tools:
                        tool_paths = ToolCategoryService._extract_tool_paths(new_tool)
                        should_add = False
                        for tool_path in tool_paths:
                            if tool_path in paths_to_add:
                                should_add = True
                                break

                        if should_add and new_tool not in category.tools:
                            category.tools.append(new_tool)
                            logger.info(f"创建新工具并添加到分类: {new_tool.name}")

                    logger.info(f"从 schema 导入了 {len(new_tool_ids)} 个新工具")
            except Exception as e:
                logger.error(f"从 schema 导入工具失败: {str(e)}")
                raise BusinessException(f'从 schema 导入工具失败: {str(e)}')

        logger.info(
            f"智能合并完成: 添加 {len(paths_to_add)} 个工具，更新 {len(paths_to_update)} 个工具，移除 {len(paths_to_remove)} 个工具")

