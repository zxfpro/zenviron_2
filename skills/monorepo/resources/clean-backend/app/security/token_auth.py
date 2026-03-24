"""
Token 鉴权（Header: Authorization: Bearer <token>）

Redis模式验证：
- 从Redis中验证JWT Token并解析用户信息
- 支持 scopes（["tools:read", "tools:write", "tools:execute"] 或 ["admin"] / ["*"]）
"""
from __future__ import annotations

from typing import List, Callable, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.models.login_user import LoginUser
from app.services.redis_token_service import RedisTokenService

security = HTTPBearer()


def _scopes_satisfied(current_scopes: List[str], required: List[str]) -> bool:
    """检查 scopes 是否满足要求"""
    if not required:
        return True
    current = set(current_scopes or [])
    if "*" in current or "admin" in current:
        return True
    return set(required).issubset(current)


def _verify_token_from_redis(token_value: str) -> LoginUser:
    """从Redis验证Token"""
    try:
        login_user = RedisTokenService.verify_token(token_value)
        return login_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token验证失败: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_scopes(required_scopes: List[str]) -> Callable:
    """
    返回一个 FastAPI 依赖，用于校验 Token + scopes。
    - 当 AUTH_ENABLED=false 时直接放行
    - 从 Header `Authorization: Bearer <token>` 读取 Token
    - 从Redis中验证JWT Token并解析用户信息
    """

    async def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> Optional[LoginUser]:
        if not settings.AUTH_ENABLED:
            return None

        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization Token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_value = credentials.credentials

        login_user = _verify_token_from_redis(token_value)

        user_scopes = login_user.get_scopes()

        if not _scopes_satisfied(user_scopes, required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient scope. Required: {required_scopes}, User has: {user_scopes}",
            )

        return login_user

    return dependency


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[LoginUser]:
    """
    获取当前登录用户

    用法：
    ```python
    from app.security.token_auth import get_current_user

    @router.get("/profile")
    async def get_profile(current_user: LoginUser = Depends(get_current_user)):
        return {"username": current_user.username, "user_id": current_user.user_id}
    ```
    """
    if not settings.AUTH_ENABLED:
        return None

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _verify_token_from_redis(credentials.credentials)
