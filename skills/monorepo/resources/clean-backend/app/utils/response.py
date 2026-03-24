"""
统一响应格式（FastAPI 版本）
"""
from typing import Any, Optional, TypeVar, Generic
from pydantic import BaseModel


T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int
    message: str
    data: Optional[T] = None


class PaginatedData(BaseModel, Generic[T]):
    """分页数据模型"""
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


def success_response(data: Any = None, message: str = '操作成功', code: int = 200) -> dict:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: HTTP状态码
        
    Returns:
        响应字典
    """
    return {
        'code': code,
        'message': message,
        'data': data
    }


def error_response(message: str = '操作失败', code: int = 400, data: Any = None) -> dict:
    """
    错误响应
    
    Args:
        message: 错误消息
        code: HTTP状态码
        data: 额外数据
        
    Returns:
        响应字典
    """
    return {
        'code': code,
        'message': message,
        'data': data
    }


def paginated_response(items: list, total: int, page: int, page_size: int, message: str = '查询成功') -> dict:
    """
    分页响应
    
    Args:
        items: 数据列表
        total: 总数量
        page: 当前页码
        page_size: 每页大小
        message: 响应消息
        
    Returns:
        分页响应字典
    """
    data = {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }
    return success_response(data, message)

