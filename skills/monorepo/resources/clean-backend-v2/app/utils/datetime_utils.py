"""
时间工具函数

统一使用北京时间（UTC+8）作为系统时间
"""
from datetime import datetime, timezone, timedelta


# 北京时区（UTC+8）
BEIJING_TZ = timezone(timedelta(hours=8))


def get_beijing_time() -> datetime:
    """
    获取当前北京时间（UTC+8）
    
    Returns:
        当前北京时间的 datetime 对象（naive，无时区信息）
    """
    # 获取 UTC 时间并转换为北京时间
    utc_now = datetime.now(timezone.utc)
    beijing_now = utc_now.astimezone(BEIJING_TZ)
    # 返回 naive datetime（数据库存储不需要时区信息）
    return beijing_now.replace(tzinfo=None)


