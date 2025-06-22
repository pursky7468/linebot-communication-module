"""FastAPI 路由定義

定義所有的 API 端點和路由
"""

from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent
from typing import Annotated
from loguru import logger

from linebot_module.config.settings import settings
from linebot_module.interfaces.message_handler import IMessageHandler
from linebot_module.infrastructure.line_api_service import LineApiService, MessageConverter
from linebot_module.application.services.message_router import MessageRouterService
from linebot_module.application.dependencies import (
    get_line_api_service, get_message_converter
)
from linebot_module.domain.models import SendMessageRequest, SendMessageResponse

# 建立路由器
router = APIRouter()

# LINE Webhook 處理器
webhook_handler = WebhookHandler(settings.line_channel_secret)


@router.post("/webhook")
async def line_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    message_handler: Annotated[IMessageHandler, Depends()],
    line_api_service: Annotated[LineApiService, Depends(get_line_api_service)],
    message_converter: Annotated[MessageConverter, Depends(get_message_converter)]
):
    """LINE Webhook 端點
    
    接收來自 LINE 平台的訊息事件
    """
    try:
        # 取得請求內容
        body = await request.body()
        signature = request.headers.get('X-Line-Signature', '')
        
        # 驗證簽章
        try:
            webhook_handler.handle(body.decode('utf-8'), signature)
        except InvalidSignatureError:
            logger.error("❌ 無效的 LINE 簽章")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # 解析事件
        events = webhook_handler.parser.parse(body.decode('utf-8'), signature)
        
        # 處理每個事件
        for event in events:
            if isinstance(event, MessageEvent):
                # 在背景任務中處理訊息
                background_tasks.add_task(
                    process_message_event,
                    event,
                    message_handler,
                    line_api_service,
                    message_converter
                )
        
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        logger.error(f"❌ 處理 webhook 時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_message_event(
    event: MessageEvent,
    message_handler: IMessageHandler,
    line_api_service: LineApiService,
    message_converter: MessageConverter
):
    """處理訊息事件的背景任務"""
    try:
        logger.info(f"📨 收到訊息事件: {event.message.type} from {event.source.user_id}")
        
        # 轉換為領域模型
        domain_message = message_converter.from_line_message(event)
        
        if domain_message:
            # 建立訊息路由服務
            router_service = MessageRouterService(line_api_service)
            
            # 處理訊息並回覆
            await router_service.process_and_reply(
                domain_message,
                message_handler,
                event.reply_token
            )
        else:
            logger.warning("⚠️ 無法轉換訊息，可能是不支援的訊息類型")
            
    except Exception as e:
        logger.error(f"❌ 處理訊息事件時發生錯誤: {e}")


@router.post("/send-message", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    line_api_service: Annotated[LineApiService, Depends(get_line_api_service)]
):
    """發送訊息端點
    
    主動發送訊息給指定使用者
    """
    try:
        logger.info(f"📤 發送訊息請求: {request.message_type} to {request.user_id}")
        
        # 根據訊息類型發送
        if request.message_type.value == "text":
            result = await line_api_service.send_text_message(
                request.user_id,
                request.content
            )
        else:
            # 其他類型暫不支援
            result = SendMessageResponse(
                success=False,
                error_message=f"不支援的訊息類型: {request.message_type}"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 發送訊息時發生錯誤: {e}")
        return SendMessageResponse(
            success=False,
            error_message=f"發送失敗: {str(e)}"
        )


@router.get("/user/{user_id}")
async def get_user_profile(
    user_id: str,
    line_api_service: Annotated[LineApiService, Depends(get_line_api_service)]
):
    """取得使用者資料端點"""
    try:
        user = await line_api_service.get_user_profile(user_id)
        
        if user:
            return user.dict()
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except Exception as e:
        logger.error(f"❌ 取得使用者資料時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": "linebot-communication-module",
        "version": "1.0.0"
    }