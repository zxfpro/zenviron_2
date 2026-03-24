"""
应用配置
"""
import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_project_root():
    """获取项目根目录"""

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)


    possible_roots = [
        project_root,
        os.getcwd(),
        '/app',
        '.',
    ]

    for root in possible_roots:
        env_path = os.path.join(root, '.env')
        if os.path.exists(env_path):
            logger.info(f"找到项目根目录: {root}")
            return root

    logger.info(f"使用计算的项目根目录: {project_root}")
    return project_root

BASE_DIR = get_project_root()


def load_env_file():
    """加载.env文件，支持多个可能的位置"""

    possible_env_files = [
        os.getenv('ENV_FILE'),
        os.path.join(BASE_DIR, '.env'),
        os.path.join(os.getcwd(), '.env'),
        '/app/.env',
        '.env',
    ]

    for env_file in possible_env_files:
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file, override=True)
            logger.info(f"✓ 已加载环境变量文件: {env_file}")
            return env_file

    logger.warning("✗ 未找到.env文件，将使用系统环境变量和默认值")
    logger.warning(f"  查找的路径: {possible_env_files}")
    return None

loaded_env = load_env_file()


class Settings(BaseSettings):
    """应用配置（使用 Pydantic Settings）"""
    

    APP_NAME: str = "Tool Server"
    VERSION: str = "1.0.0"

    _ENV: str = os.getenv('APP_ENV','production')
    DEBUG: bool = _ENV == 'development'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    def __init__(self, **kwargs):
        """初始化配置并记录日志"""
        super().__init__(**kwargs)
        self._log_config_loaded()

    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '3306'))
    DB_USER: str = os.getenv('DB_USER', 'root')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    DB_NAME: str = os.getenv('DB_NAME', 'test_db')

    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = DEBUG

    SERVER_HOST: str = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', '5000'))

    TOOL_REQUEST_TIMEOUT: int = int(os.getenv('TOOL_REQUEST_TIMEOUT', '30'))
    TOOL_MAX_RETRIES: int = int(os.getenv('TOOL_MAX_RETRIES', '3'))

    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR: str = os.getenv('LOG_DIR', 'logs')
    LOG_ENABLE_FILE: bool = os.getenv('LOG_ENABLE_FILE', 'true').lower() == 'true'
    LOG_ENABLE_CONSOLE: bool = os.getenv('LOG_ENABLE_CONSOLE', 'true').lower() == 'true'
    LOG_MAX_BYTES: int = int(os.getenv('LOG_MAX_BYTES', str(10 * 1024 * 1024)))
    LOG_BACKUP_COUNT: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))

    RATE_LIMIT_ENABLED: bool = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_DEFAULT: str = os.getenv('RATE_LIMIT_DEFAULT', '60/minute')
    RATE_LIMIT_STORAGE_URI: str = os.getenv('RATE_LIMIT_STORAGE_URI', 'memory://')

    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB: int = int(os.getenv('REDIS_DB', '0'))
    REDIS_PASSWORD: str = os.getenv('REDIS_PASSWORD', '')
    REDIS_DECODE_RESPONSES: bool = True

    REDIS_TOKEN_KEY_PREFIX: str = os.getenv('REDIS_TOKEN_KEY_PREFIX', 'login_tokens:')

    TOKEN_EXPIRE_TIME: int = int(os.getenv('TOKEN_EXPIRE_TIME', '-1'))


    JWT_SECRET: str = os.getenv('JWT_SECRET', 'abcdefghijklmnopqrstuvwxyz')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS512')


    AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "true").lower() == "true"
    
    def _log_config_loaded(self):
        """记录配置加载信息"""
        logger.info("=" * 60)
        logger.info("配置加载完成")
        logger.info("=" * 60)
        logger.info(f"应用名称: {self.APP_NAME} v{self.VERSION}")
        logger.info(f"运行环境: {self._ENV} ({'开发模式' if self.DEBUG else '生产模式'})")
        logger.info(f"数据库: {self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME} (用户: {self.DB_USER})")
        logger.info(f"服务器: {self.SERVER_HOST}:{self.SERVER_PORT}")
        logger.info(f"日志级别: {self.LOG_LEVEL}, 文件日志: {self.LOG_ENABLE_FILE}, 控制台日志: {self.LOG_ENABLE_CONSOLE}")
        logger.info(f"AUTH_ENABLED={self.AUTH_ENABLED}")
        

        if self.RATE_LIMIT_ENABLED:
            logger.info(f"速率限制: 已启用 (默认: {self.RATE_LIMIT_DEFAULT}, 存储: {self.RATE_LIMIT_STORAGE_URI})")
        else:
            logger.warning("速率限制: 已禁用")


        if self.AUTH_ENABLED:
            logger.info(f"Token 认证: Redis模式 (Redis: {self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB})")
        else:
            logger.warning("Token 认证: 已禁用（生产环境不推荐）")


        if self.DEBUG:
            logger.warning("⚠️  运行在开发模式，某些安全功能可能被禁用")
        else:
            if self.SECRET_KEY == 'dev-secret-key-change-in-production':
                logger.warning("⚠️  SECRET_KEY 使用默认值，生产环境请修改！")
        
        logger.info("=" * 60)
    
    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    
    class Config:
        case_sensitive = True


settings = Settings()

