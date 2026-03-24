"""
Redis Token 验证服务

从Redis中验证Token并解析LoginUser信息
支持JSON格式和Java序列化格式
"""
from __future__ import annotations

import json
import logging
import re
from typing import Optional

import jwt
from app.config import settings
from app.models.login_user import LoginUser
from app.utils.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class RedisTokenService:
    """Redis Token验证服务"""

    @staticmethod
    def get_redis_key(token: str) -> str:
        """获取Redis中Token的key"""
        return f"{settings.REDIS_TOKEN_KEY_PREFIX}{token}"

    @staticmethod
    def verify_token(jwt_token: str) -> Optional[LoginUser]:
        """
        验证Token并返回LoginUser信息

        流程：
        1. 解析JWT Token，提取 login_user_key
        2. 使用 login_user_key 作为Redis key查询

        Args:
            jwt_token: JWT Token字符串（完整的JWT）

        Returns:
            LoginUser对象，如果验证失败返回None

        Raises:
            ValueError: Token格式错误或已过期
        """
        if not jwt_token:
            raise ValueError("Token不能为空")

        try:
            login_user_key = RedisTokenService._extract_login_user_key(jwt_token)

            if not login_user_key:
                raise ValueError("JWT Token中未找到login_user_key字段")

            logger.info(f"从JWT Token提取login_user_key: {login_user_key}")

            redis_client = get_redis_client()
            redis_key = RedisTokenService.get_redis_key(login_user_key)

            logger.info(f"从Redis中获取Token数据: {redis_key}")
            token_data = redis_client.get(redis_key)

            if not token_data:
                logger.warning(f"Token不存在于Redis: {redis_key}")
                raise ValueError("Token无效或已过期")

            login_user = RedisTokenService._parse_token_data(token_data)

            if not login_user:
                logger.error(f"Token数据解析失败: {redis_key}")
                raise ValueError("Token数据格式错误")

            if login_user.is_expired():
                logger.warning(f"Token已过期: {redis_key}, expire_time={login_user.expire_time}")
                raise ValueError("Token已过期")

            logger.info(f"Token验证成功: user_id={login_user.user_id}, username={login_user.username}")
            return login_user

        except ValueError as e:
            raise
        except Exception as e:
            logger.error(f"Token验证过程中发生错误: {str(e)}", exc_info=True)
            raise ValueError(f"Token验证失败: {str(e)}")

    @staticmethod
    def _extract_login_user_key(jwt_token: str) -> Optional[str]:
        """
        从JWT Token中提取login_user_key

        Args:
            jwt_token: JWT Token字符串

        Returns:
            login_user_key (UUID)，解析失败返回None

        Raises:
            ValueError: Token格式错误或解析失败
        """
        """
        兼容两种输入：
        1) 完整JWT：从payload里取 login_user_key
        2) 直接传 login_user_key（UUID）：直接作为 redis key 使用（避免 Not enough segments）

        说明：Redis 校验以 redis 中是否存在/是否过期为准，因此这里只需要"解析payload"，不强依赖 JWT 密钥/算法匹配。
        """
        if not jwt_token:
            raise ValueError("Token不能为空")

        token = jwt_token.strip()
        if token.startswith("Bearer "):
            token = token[7:].strip()

        logger.info(f"解析JWT Token: {token[:50]}..." if len(token) > 50 else f"解析JWT Token: {token}")

        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            logger.info(f"JWT Token payload: {payload}")

            login_user_key = payload.get("login_user_key")
            if not login_user_key:
                raise ValueError(f"JWT Token中未找到login_user_key字段。Payload中的字段: {list(payload.keys())}")

            return login_user_key

        except jwt.DecodeError as e:
            raise ValueError(f"JWT Token解析失败: {str(e)}")
        except Exception as e:
            logger.error(f"解析Token以提取login_user_key失败: {str(e)}", exc_info=True)
            raise ValueError(f"解析Token失败: {str(e)}")


    @staticmethod
    def _parse_token_data(token_data: str | bytes) -> Optional[LoginUser]:
        """
        解析Token数据

        支持两种格式：
        1. FastJSON格式字符串（Java的fastjson库序列化）
        2. Java序列化对象（需要javaobj-py3库）

        Args:
            token_data: 从Redis获取的数据

        Returns:
            LoginUser对象，解析失败返回None
        """
        if isinstance(token_data, bytes):
            try:
                token_data_str = token_data.decode('utf-8')
            except UnicodeDecodeError:

                return RedisTokenService._parse_java_serialized(token_data)
        else:
            token_data_str = token_data

        try:
            cleaned_str = RedisTokenService._clean_fastjson(token_data_str)

            data_dict = json.loads(cleaned_str)

            if 'user' in data_dict and data_dict['user']:
                logger.info(f"🔍 user.roles: {data_dict['user'].get('roles', [])}")

            login_user = LoginUser.from_dict(data_dict)
            return login_user

        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"FastJSON解析失败，尝试Java序列化格式: {str(e)}")
            return RedisTokenService._parse_java_serialized(token_data)

    @staticmethod
    def _clean_fastjson(fastjson_str: str) -> str:
        """
        清理FastJSON字符串，转换为标准JSON格式

        处理FastJSON特有的语法：
        1. Set["a", "b"] → ["a", "b"]
        2. 106L → 106
        3. 保留@type字段（不影响解析）

        Args:
            fastjson_str: FastJSON格式的字符串

        Returns:
            标准JSON格式的字符串
        """

        cleaned = fastjson_str.strip()

        cleaned = re.sub(r'Set\[(.*?)\]', r'[\1]', cleaned)

        cleaned = re.sub(r'(\d+)L', r'\1', cleaned)

        return cleaned

    @staticmethod
    def _parse_java_serialized(token_data: bytes) -> Optional[LoginUser]:
        """
        解析Java序列化对象

        需要安装javaobj-py3库：
        pip install javaobj-py3

        Args:
            token_data: Java序列化的二进制数据

        Returns:
            LoginUser对象，解析失败返回None
        """
        try:
            import javaobj

            java_obj = javaobj.loads(token_data)

            if hasattr(java_obj, '__dict__'):
                data_dict = java_obj.__dict__
            else:
                data_dict = {}
                for attr in dir(java_obj):
                    if not attr.startswith('_') and not callable(getattr(java_obj, attr)):
                        try:
                            data_dict[attr] = getattr(java_obj, attr)
                        except Exception:
                            pass

            return LoginUser.from_dict(data_dict)

        except ImportError:
            logger.warning(
                "未安装javaobj-py3库，无法解析Java序列化对象。"
                "如需支持Java序列化格式，请运行: pip install javaobj-py3"
            )
            return None
        except Exception as e:
            logger.error(f"Java序列化对象解析失败: {str(e)}", exc_info=True)
            return None
