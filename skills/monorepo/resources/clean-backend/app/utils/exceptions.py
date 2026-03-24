"""
自定义异常
"""


class BusinessException(Exception):
    """业务异常基类"""
    
    def __init__(self, message, code=400):
        """
        初始化业务异常
        
        Args:
            message: 异常消息
            code: HTTP状态码
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


class ToolNotFoundException(BusinessException):
    """工具不存在异常"""
    
    def __init__(self, tool_id):
        super().__init__(f'工具不存在: {tool_id}', 404)


class ToolNameDuplicateException(BusinessException):
    """工具名称重复异常"""
    
    def __init__(self, name):
        super().__init__(f'工具名称已存在: {name}', 400)


class ToolInUseException(BusinessException):
    """工具正在使用异常"""
    
    def __init__(self, tool_name):
        super().__init__(f'工具正在使用中，无法删除: {tool_name}', 400)


class InvalidSchemaException(BusinessException):
    """无效的Schema异常"""
    
    def __init__(self, detail):
        super().__init__(f'无效的Schema配置: {detail}', 400)


class ToolExecutionException(BusinessException):
    """工具执行异常"""
    
    def __init__(self, tool_name, detail):
        super().__init__(f'工具执行失败 [{tool_name}]: {detail}', 500)


class ToolDisabledException(BusinessException):
    """工具已停用异常"""
    
    def __init__(self, tool_name):
        super().__init__(f'工具已停用: {tool_name}', 400)


class CategoryDisabledException(BusinessException):
    """工具分类已停用异常"""
    
    def __init__(self, category_name):
        super().__init__(f'工具所属分类已停用: {category_name}', 400)

