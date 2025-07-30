"""
提肛小助手后端主程序
FastAPI应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging

from api.routes import router as api_router
from services.scheduler import SchedulerService
from models.database import init_database
from utils.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="提肛小助手 API",
    description="现代化的提肛运动辅助软件后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite默认端口
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")

# 静态文件服务（如果需要）
# app.mount("/static", StaticFiles(directory="static"), name="static")

# 全局变量存储调度器实例
scheduler_service = None

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    try:
        # 初始化数据库
        logger.info("正在初始化数据库...")
        init_database()
        logger.info("✅ 数据库初始化完成")

        # 启动调度器服务
        global scheduler_service
        scheduler_service = SchedulerService()
        scheduler_service.start()
        logger.info("✅ 调度器服务启动完成")

        logger.info("🚀 提肛小助手后端服务启动成功!")
        logger.info(f"📖 API文档地址: http://{settings.HOST}:{settings.PORT}/docs")

    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    try:
        global scheduler_service
        if scheduler_service:
            scheduler_service.stop()
            logger.info("✅ 调度器服务已停止")

        logger.info("👋 提肛小助手后端服务已关闭!")

    except Exception as e:
        logger.error(f"❌ 服务关闭时出错: {e}")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "提肛小助手 API 服务运行中",
        "version": "1.0.0",
        "status": "healthy",
        "docs": f"http://{settings.HOST}:{settings.PORT}/docs",
        "scheduler_status": scheduler_service.get_scheduler_status() if scheduler_service else None
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        from models.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        db_status = "unhealthy"

    # 检查调度器状态
    scheduler_status = "healthy" if scheduler_service and scheduler_service.is_running else "stopped"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "kegel-helper-api",
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "scheduler": scheduler_status
        },
        "timestamp": "2024-01-01T00:00:00Z"  # 实际应用中使用真实时间戳
    }

@app.get("/api/v1/system/info")
async def get_system_info():
    """获取系统信息"""
    import platform
    import psutil

    try:
        return {
            "success": True,
            "data": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent if platform.system() != "Windows" else psutil.disk_usage('C:').percent,
                "scheduler_status": scheduler_service.get_scheduler_status() if scheduler_service else None
            }
        }
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        return {
            "success": False,
            "message": f"获取系统信息失败: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
