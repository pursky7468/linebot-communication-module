"""依賴注入設定

設定 FastAPI 的依賴注入系統，實現控制反轉
"""

from fastapi import FastAPI, Depends
from typing import Annotated

from linebot_module.interfaces.message_handler import IMessageHandler, IMessageRouter
from linebot_module.infrastructure.line_api_service import LineApiService, MessageConverter
from linebot_module.application.services.message_router import MessageRouterService


def get_line_api_service() -> LineApiService:
    """取得 LINE API 服務實例"""
    return LineApiService()


def get_message_converter() -> MessageConverter:
    """取得訊息轉換器實例"""
    return MessageConverter()


def get_message_router(
    line_api_service: Annotated[LineApiService, Depends(get_line_api_service)]
) -> IMessageRouter:
    """取得訊息路由器實例"""
    return MessageRouterService(line_api_service)


class DefaultMessageHandler(IMessageHandler):
    """預設訊息處理器 - 示範用途"""
    
    async def handle_text_message(self, message) -> str:
        """處理文字訊息 - 簡單回應"""
        return f"收到您的訊息：{message.text}"
    
    async def handle_image_message(self, message) -> str:
        """處理圖片訊息 - 簡單回應"""
        return "收到圖片訊息，謝謝分享！"


def get_default_message_handler() -> IMessageHandler:
    """取得預設訊息處理器 (可以被覆寫)"""
    return DefaultMessageHandler()


def setup_dependencies(app: FastAPI) -> None:
    """設定應用程式的依賴注入
    
    Args:
        app: FastAPI 應用程式實例
    """
    # 註冊預設的訊息處理器
    # 外部模組可以透過 app.dependency_overrides 覆寫這個設定
    app.dependency_overrides[IMessageHandler] = get_default_message_handler