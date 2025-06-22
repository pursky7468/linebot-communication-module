"""LINE BOT 通訊模組主程式

啟動 FastAPI 應用程式並設定所有必要的路由與中介軟體
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from linebot_module.config.settings import settings
from linebot_module.application.api import router as api_router
from linebot_module.application.dependencies import setup_dependencies

# 建立 FastAPI 應用程式實例
app = FastAPI(
    title="LINE BOT 通訊模組",
    description="基於 Clean Architecture 設計的 LINE BOT 通訊模組，專門負責與 LINE 平台的訊息收發功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 設定 CORS 中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制特定網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定依賴注入
setup_dependencies(app)

# 註冊 API 路由
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """應用程式啟動事件"""
    logger.info("🚀 LINE BOT 通訊模組啟動中...")
    logger.info(f"📡 伺服器設定: {settings.host}:{settings.port}")
    logger.info(f"🔧 偵錯模式: {settings.debug}")
    if settings.ngrok_url:
        logger.info(f"🌐 ngrok 網址: {settings.ngrok_url}")
    logger.info("✅ 應用程式啟動完成")


@app.on_event("shutdown")
async def shutdown_event():
    """應用程式關閉事件"""
    logger.info("🛑 LINE BOT 通訊模組關閉中...")
    logger.info("✅ 應用程式已安全關閉")


@app.get("/")
async def root():
    """根路徑端點 - 健康檢查"""
    return {
        "message": "LINE BOT 通訊模組運行中",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "timestamp": settings.log_level,
        "service": "linebot-communication-module"
    }


if __name__ == "__main__":
    # 直接執行時啟動伺服器
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )