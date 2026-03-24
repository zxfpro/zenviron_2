"""
日志配置模块

提供统一的日志配置，支持：
- 文件日志（带轮转）
- 控制台日志
- 不同日志级别的分离
- 结构化日志格式
"""
import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from app.config import settings


def setup_logging(
    log_dir: Optional[str] = None,
    log_level: Optional[str] = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    配置应用日志系统
    
    Args:
        log_dir: 日志目录路径，默认为项目根目录下的 logs 目录
        log_level: 日志级别，默认为配置中的 LOG_LEVEL
        enable_file_logging: 是否启用文件日志
        enable_console_logging: 是否启用控制台日志
        max_bytes: 单个日志文件最大大小（字节），默认 10MB
        backup_count: 保留的备份文件数量，默认 5 个
    """
    if log_level is None:
        log_level = settings.LOG_LEVEL.upper()

    numeric_level = getattr(logging, log_level, logging.INFO)

    if log_dir is None:
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
    else:
        log_dir = Path(log_dir)

    if enable_file_logging:
        log_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    root_logger.handlers.clear()

    detailed_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if enable_console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(simple_format)
        root_logger.addHandler(console_handler)

    if enable_file_logging:
        app_log_file = log_dir / "app.log"
        app_handler = logging.handlers.RotatingFileHandler(
            filename=str(app_log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        app_handler.setLevel(numeric_level)
        app_handler.setFormatter(detailed_format)
        root_logger.addHandler(app_handler)

        error_log_file = log_dir / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            filename=str(error_log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_format)
        root_logger.addHandler(error_handler)

        access_log_file = log_dir / "access.log"
        access_handler = logging.handlers.RotatingFileHandler(
            filename=str(access_log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        access_handler.setLevel(logging.INFO)
        access_format = logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        access_handler.setFormatter(access_format)

        access_logger = logging.getLogger("access")
        access_logger.setLevel(logging.INFO)
        access_logger.addHandler(access_handler)
        access_logger.propagate = False

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("gunicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"日志系统初始化完成 - 级别: {log_level}, 文件日志: {enable_file_logging}, 控制台日志: {enable_console_logging}")
    if enable_file_logging:
        logger.info(f"日志目录: {log_dir}")


def get_access_logger():
    """
    获取访问日志记录器（用于记录 API 请求）
    
    Returns:
        访问日志记录器
    """
    return logging.getLogger("access")

