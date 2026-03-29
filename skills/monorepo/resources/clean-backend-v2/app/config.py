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
ENV_FILE = '.env'



def load_env_file(env_file):
    """加载.env文件，支持多个可能的位置"""

        
    if env_file and os.path.exists(env_file):
        load_dotenv(env_file, override=True)
        logger.info(f"✓ 已加载环境变量文件: {env_file}")
        return env_file

    logger.warning("✗ 未找到.env文件，将使用系统环境变量和默认值")
    return None

loaded_env = load_env_file(ENV_FILE) 


class Settings(BaseSettings):
    """应用配置（使用 Pydantic Settings）"""
    

    APP_NAME: str = "PostPin"
    VERSION: str = "1.0.0"
    APP_PATCH_VERSION: str = os.getenv("APP_PATCH_VERSION", "v1")

    _ENV: str = os.getenv('APP_ENV','production')
    DEBUG: bool = _ENV == 'development'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    def __init__(self, **kwargs):
        """初始化配置并记录日志"""
        super().__init__(**kwargs)
        self._log_config_loaded()

    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '3306'))
    MYSQL_USER: str = os.getenv('MYSQL_USER', 'root')
    MYSQL_ROOT_PASSWORD: str = os.getenv('MYSQL_ROOT_PASSWORD', '')
    MYSQL_DATABASE: str = os.getenv('MYSQL_DATABASE', 'test_db')
    MYSQL_PASSWORD: str = os.getenv('MYSQL_PASSWORD', 'postpin12345')

    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = DEBUG

    SERVER_HOST: str = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', '8888'))

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
    
    #new
    TOS_BUCKET: str = os.getenv('TOS_BUCKET', '')
    TOS_AK: str = os.getenv('TOS_AK', '')
    TOS_SK: str = os.getenv('TOS_SK', '')
    TOS_ENDPOINT: str = os.getenv('TOS_ENDPOINT', '')
    TOS_REGION: str = os.getenv('TOS_REGION', '')

    SMTP: str = os.getenv('SMTP', '')
    sender: str = os.getenv('sender', '')
    V_API_BASE_URL: str = os.getenv('V_API_BASE_URL', '')
    V_API_API_KEY: str = os.getenv('V_API_API_KEY', '')
    BIANXIE_BASE: str = os.getenv('BIANXIE_BASE', '')
    BIANXIE_API_KEY: str = os.getenv('BIANXIE_API_KEY', '')


    def _log_config_loaded(self):
        """记录配置加载信息"""
        logger.info("=" * 60)
        logger.info("配置加载完成")
        logger.info("=" * 60)
        logger.info(f"应用名称: {self.APP_NAME} v{self.VERSION}")
        logger.info(f"运行环境: {self._ENV} ({'开发模式' if self.DEBUG else '生产模式'})")
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
    
    
    class Config:
        case_sensitive = True


settings = Settings()
