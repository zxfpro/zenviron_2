"""
速率限制配置模块

提供 API 速率限制功能，防止 API 滥用和 DDoS 攻击。
使用 slowapi 库实现基于 IP 地址的速率限制。
"""
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status

_limiter: Optional[Limiter] = None


def get_client_ip(request: Request) -> str:
    """
    获取客户端真实 IP 地址
    
    优先从 X-Forwarded-For 或 X-Real-IP 头获取（适用于反向代理场景）
    否则使用 request.client.host
    
    Args:
        request: FastAPI 请求对象
        
    Returns:
        客户端 IP 地址
    """

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    return get_remote_address(request)


def create_limiter() -> Limiter:
    """
    创建并配置速率限制器
    
    Returns:
        配置好的 Limiter 实例
    """
    # 使用自定义的 IP 获取函数
    limiter = Limiter(key_func=get_client_ip)
    return limiter


def get_rate_limit_key(request: Request) -> str:
    """
    获取速率限制的键（用于识别请求来源）
    
    优先使用 Token（如果已认证），否则使用 IP 地址
    这样可以实现基于 Token 的速率限制，而不是仅基于 IP
    
    Args:
        request: FastAPI 请求对象
        
    Returns:
        速率限制键
    """
    # 尝试从请求头获取 Token
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]  # 移除 "Bearer " 前缀
        if token:
            # 使用 Token 作为限制键（同一 Token 共享限制）
            return f"token:{token[:8]}"  # 只使用前8位，避免暴露完整 Token
    
    # 如果没有 Token，使用 IP 地址
    return get_client_ip(request)


def get_limiter(storage_uri: str = "memory://") -> Limiter:
    """
    获取或创建速率限制器实例（延迟初始化）
    
    延迟初始化可以避免在模块导入时读取 .env 文件导致的编码问题
    
    Args:
        storage_uri: 存储后端 URI，默认为内存存储
        
    Returns:
        Limiter 实例
    """
    import os
    global _limiter
    if _limiter is None:
        # 临时修复 starlette.Config 的编码问题
        # slowapi 使用 starlette.Config，它会自动读取 .env 文件
        # 在 Windows 上默认使用 GBK 编码，导致 UTF-8 文件读取失败
        try:
            from starlette import config as starlette_config
            original_read_file = starlette_config.Config._read_file
            
            def _read_file_utf8(self, env_file):
                """使用 UTF-8 编码读取文件"""
                if not os.path.exists(env_file):
                    return {}
                file_values = {}
                try:
                    with open(env_file, 'r', encoding='utf-8') as input_file:
                        for line in input_file.readlines():
                            line = line.strip()
                            if not line or line.startswith('#'):
                                continue
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")
                                file_values[key] = value
                except (UnicodeDecodeError, IOError):
                    # 如果读取失败，返回空字典
                    pass
                return file_values
            
            # 临时替换 _read_file 方法
            starlette_config.Config._read_file = _read_file_utf8
            
            try:
                # 延迟创建，现在会使用 UTF-8 编码读取 .env 文件
                _limiter = Limiter(
                    key_func=get_rate_limit_key,
                    storage_uri=storage_uri,
                    default_limits=[]  # 不在全局设置默认限制，由各路由单独设置
                )
            finally:
                # 恢复原始方法
                starlette_config.Config._read_file = original_read_file
        except Exception as e:
            # 如果修复失败，尝试使用不存在的文件路径
            original_env_file = os.environ.get("ENV_FILE")
            try:
                # 使用一个不存在的文件路径
                os.environ["ENV_FILE"] = os.path.join(os.path.dirname(__file__), ".env_not_exist")
                _limiter = Limiter(
                    key_func=get_rate_limit_key,
                    storage_uri=storage_uri,
                    default_limits=[]
                )
            finally:
                if original_env_file is not None:
                    os.environ["ENV_FILE"] = original_env_file
                elif "ENV_FILE" in os.environ:
                    del os.environ["ENV_FILE"]
    return _limiter


# 延迟初始化：不在模块级别创建，避免编码问题
# 实际使用时会在 register_rate_limiting 中正确初始化
# 路由装饰器会通过 LazyLimiter 包装器访问
limiter: Optional[Limiter] = None


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    自定义速率限制超出异常处理器
    
    Args:
        request: FastAPI 请求对象
        exc: 速率限制超出异常
        
    Returns:
        HTTP 响应
    """
    # 记录速率限制触发事件
    import logging
    logger = logging.getLogger(__name__)
    client_ip = get_client_ip(request)
    logger.warning(
        f"速率限制触发: {request.method} {request.url.path} - "
        f"IP: {client_ip} - "
        f"限制: {exc.detail if hasattr(exc, 'detail') else str(exc)}"
    )
    
    # 从异常中提取信息
    retry_after = getattr(exc, 'retry_after', 60)
    limit = getattr(exc, 'limit', '')
    
    # 返回标准化的错误响应
    from fastapi.responses import JSONResponse
    from app.utils.response import error_response
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=error_response(
            message="请求过于频繁，请稍后再试",
            code=429
        ),
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": "0"
        }
    )


# 预定义的速率限制规则
RATE_LIMIT_RULES = {
    # 默认限制：每分钟 60 次请求
    "default": "60/minute",
    
    # 工具执行接口：每分钟 30 次（较严格，因为可能涉及外部 API 调用）
    "tool_execute": "30/minute",
    
    # 工具测试接口：每分钟 20 次（更严格，避免测试滥用）
    "tool_test": "20/minute",
    
    # 工具列表/查询接口：每分钟 120 次（较宽松，主要是查询操作）
    "tool_read": "120/minute",
    
    # 工具创建/更新/删除接口：每分钟 10 次（严格，避免误操作）
    "tool_write": "10/minute",
    
    # 健康检查接口：每分钟 300 次（非常宽松，用于监控）
    "health": "300/minute",
}

