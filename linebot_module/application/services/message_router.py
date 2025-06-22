"""訊息路由服務

實作訊息路由邏輯，將不同類型的訊息分發到對應的處理器
"""

from typing import Optional
from loguru import logger

from linebot_module.interfaces.message_handler import IMessageRouter, IMessageHandler
from linebot_module.infrastructure.line_api_service import LineApiService
from linebot_module.domain.models import (
    BaseMessage, TextMessage, ImageMessage, AudioMessage, 
    VideoMessage, LocationMessage, StickerMessage, MessageType
)


class MessageRouterService(IMessageRouter):
    """訊息路由服務實作"""
    
    def __init__(self, line_api_service: LineApiService):
        """初始化訊息路由服務
        
        Args:
            line_api_service: LINE API 服務實例
        """
        self.line_api_service = line_api_service
    
    async def route_message(
        self, 
        message: BaseMessage, 
        message_handler: IMessageHandler
    ) -> Optional[str]:
        """路由訊息到對應的處理器
        
        Args:
            message: 訊息物件
            message_handler: 訊息處理器
            
        Returns:
            Optional[str]: 處理結果，None 表示不回應
        """
        try:
            logger.info(f"📨 路由訊息: {message.message_type} from {message.user_id}")
            
            # 根據訊息類型路由到對應的處理器
            if message.message_type == MessageType.TEXT and isinstance(message, TextMessage):
                return await message_handler.handle_text_message(message)
            
            elif message.message_type == MessageType.IMAGE and isinstance(message, ImageMessage):
                return await message_handler.handle_image_message(message)
            
            elif message.message_type == MessageType.AUDIO and isinstance(message, AudioMessage):
                return await message_handler.handle_audio_message(message)
            
            elif message.message_type == MessageType.VIDEO and isinstance(message, VideoMessage):
                return await message_handler.handle_video_message(message)
            
            elif message.message_type == MessageType.LOCATION and isinstance(message, LocationMessage):
                return await message_handler.handle_location_message(message)
            
            elif message.message_type == MessageType.STICKER and isinstance(message, StickerMessage):
                return await message_handler.handle_sticker_message(message)
            
            else:
                logger.warning(f"⚠️ 未知的訊息類型: {message.message_type}")
                return await message_handler.handle_unknown_message(message)
                
        except Exception as e:
            logger.error(f"❌ 路由訊息時發生錯誤: {e}")
            return "抱歉，處理您的訊息時發生錯誤，請稍後再試。"
    
    async def process_and_reply(
        self, 
        message: BaseMessage, 
        message_handler: IMessageHandler,
        reply_token: str
    ) -> bool:
        """處理訊息並自動回覆
        
        Args:
            message: 訊息物件
            message_handler: 訊息處理器
            reply_token: 回覆 token
            
        Returns:
            bool: 處理是否成功
        """
        try:
            # 路由訊息並取得回應內容
            response_content = await self.route_message(message, message_handler)
            
            # 如果有回應內容，則發送回覆
            if response_content:
                result = await self.line_api_service.reply_message(
                    reply_token, 
                    response_content
                )
                return result.success
            else:
                logger.info("📤 沒有回應內容，不發送回覆")
                return True
                
        except Exception as e:
            logger.error(f"❌ 處理並回覆訊息時發生錯誤: {e}")
            return False