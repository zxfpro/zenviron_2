"""
FastAPI 入口文件
"""
import uvicorn
# from dotenv import load_dotenv
from app import create_app
from app.config import settings

# 加载 .env 文件
# load_dotenv()

# 创建应用实例
app = create_app()


if __name__ == '__main__':
    # 开发模式运行
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

