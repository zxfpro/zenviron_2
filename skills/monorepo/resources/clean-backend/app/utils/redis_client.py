"""
Redis 客户端管理（用于Token验证）
"""
import redis
from typing import Optional
from app.config import settings


class RedisClient:
    """Redis客户端单例"""

    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        """获取Redis客户端实例（单例模式）"""
        if cls._instance is None:
            cls._instance = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=settings.REDIS_DECODE_RESPONSES,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
        return cls._instance

    @classmethod
    def close(cls):
        """关闭Redis连接"""
        if cls._instance:
            cls._instance.close()
            cls._instance = None


def get_redis_client() -> redis.Redis:
    """获取Redis客户端（快捷方法）"""
    return RedisClient.get_client()
