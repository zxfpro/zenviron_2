import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

logger = logging.getLogger(__name__)


from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute




from app.extensions import get_session, init_db
from app.points_config import init_points_cost_rules
from app.models.admin import setup_admin

from app.api.auth import fastapi_users, router as auth_router
from app.api.points import router as points_router
from app.api.image_edit import router as image_router
from app.models import User
from app.api.auth import UserCreate, auth_backend

from app.api.wechatpay.router import router as wechatpay_router



@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    """Initialize database and points cost rules on startup."""
    async with AsyncExitStack():
        logger.info(f"应用启动: {settings.APP_NAME} v{settings.VERSION}")
        logger.info(f"运行环境: {'开发' if settings.DEBUG else '生产'}")

        if settings.AUTH_ENABLED:
            logger.info("Token 鉴权: 已启用（Redis JWT Token 验证模式）")
        else:
            logger.warning("Token 鉴权: 已禁用（所有接口无需认证即可访问）")
        
        init_db()
        session = next(get_session())
        try:
            init_points_cost_rules(session)
        finally:
            session.close()

        yield

        logger.info("应用正在关闭...")


def create_app() -> FastAPI:
    """
    创建FastAPI应用实例
    
    Returns:
        FastAPI应用实例
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=combined_lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )



    cors_origins = os.getenv('CORS_ORIGINS', '*').split(',') if not settings.DEBUG else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # if settings.RATE_LIMIT_ENABLED:
    #     register_rate_limiting(app)

    # register_request_logging_middleware(app)

    register_routers(app)

    # register_exception_handlers(app)

    # try:
    #     setup_prometheus_metrics(app)
    # except Exception as e:
    #     logger.warning(f"Prometheus metrics 配置失败（可选功能）: {str(e)}")

    
    return app


def register_request_logging_middleware(app: FastAPI):
    """
    注册请求日志中间件
    
    记录所有 API 请求的详细信息，包括：
    - 请求方法、路径
    - 响应状态码
    - 处理时间
    - 客户端 IP
    """
    access_logger = get_access_logger()
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """记录请求日志"""
        start_time = time.time()

        client_ip = request.client.host if request.client else "unknown"
        if request.headers.get("x-forwarded-for"):
            client_ip = request.headers.get("x-forwarded-for").split(",")[0].strip()
        elif request.headers.get("x-real-ip"):
            client_ip = request.headers.get("x-real-ip")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            access_logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s - "
                f"IP: {client_ip} - "
                f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
            )

            if process_time > 1.0:
                logger.warning(
                    f"慢请求检测: {request.method} {request.url.path} - "
                    f"处理时间: {process_time:.3f}s"
                )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"请求处理异常: {request.method} {request.url.path} - "
                f"Time: {process_time:.3f}s - "
                f"IP: {client_ip} - "
                f"Error: {str(e)}",
                exc_info=True
            )
            raise


def register_rate_limiting(app: FastAPI):
    """
    注册速率限制
    
    配置速率限制器和异常处理器
    """

    storage_uri = settings.RATE_LIMIT_STORAGE_URI or "memory://"

    limiter = get_limiter(storage_uri)
    
    if storage_uri != "memory://":
        logger.info(f"速率限制使用存储后端: {storage_uri}")
    else:
        logger.info("速率限制使用内存存储（单实例模式）")

    app.state.limiter = limiter

    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    
    logger.info(f"速率限制已启用 - 默认限制: {settings.RATE_LIMIT_DEFAULT}")

    import app.utils.rate_limit as rate_limit_module
    rate_limit_module.limiter = limiter


def register_routers(app: FastAPI):
    """注册路由"""
    
    @app.get("/",  tags=["系统信息"])
    async def root():
        return {
            "message": "Running",
            "version": settings.APP_PATCH_VERSION,
        }
    

    app.include_router(fastapi_users.get_auth_router(auth_backend),prefix="/auth",tags=["auth"],)
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(fastapi_users.get_register_router(User, UserCreate),prefix="/auth",tags=["auth"],)
    app.include_router(points_router)
    app.include_router(image_router)
    # app.include_router(wechatpay_router)

    setup_admin(app)



def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""
    
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        """处理业务异常"""
        return JSONResponse(
            status_code=exc.code,
            content=error_response(exc.message, exc.code)
        )
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """处理404错误"""
        return JSONResponse(
            status_code=404,
            content=error_response('资源不存在', 404)
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        """处理500错误"""
        return JSONResponse(
            status_code=500,
            content=error_response('服务器内部错误', 500)
        )
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        """处理速率限制超出异常"""
        return rate_limit_exceeded_handler(request, exc)
    
    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception):
        """处理未预期的异常"""

        error_message = '服务器内部错误' if not settings.DEBUG else f'服务器内部错误: {str(exc)}'
        return JSONResponse(
            status_code=500,
            content=error_response(error_message, 500)
        )
