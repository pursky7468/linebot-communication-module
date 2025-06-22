"""LINE Bot API 服務實作

實作與 LINE 平台的實際通訊功能
"""

import aiofiles
from typing import Optional, Union, BinaryIO
from linebot import LineBotApi
from linebot.models import (
    TextSendMessage, ImageSendMessage, MessageEvent,
    TextMessage as LineTextMessage, ImageMessage as LineImageMessage
)
from linebot.exceptions import LineBotApiError
from loguru import logger

from linebot_module.config.settings import settings
from linebot_module.domain.models import (
    BaseMessage, TextMessage, ImageMessage, SendMessageRequest, 
    SendMessageResponse, MessageType, User
)


class LineApiService:
    """LINE Bot API 服務類別"""
    
    def __init__(self):
        """初始化 LINE Bot API 客戶端"""
        self.line_bot_api = LineBotApi(settings.line_channel_access_token)
    
    async def send_text_message(self, user_id: str, text: str) -> SendMessageResponse:
        """發送文字訊息
        
        Args:
            user_id: 目標使用者 ID
            text: 訊息文字內容
            
        Returns:
            SendMessageResponse: 發送結果
        """
        try:
            message = TextSendMessage(text=text)
            self.line_bot_api.push_message(user_id, message)
            
            logger.info(f"✅ 成功發送文字訊息到使用者 {user_id}")
            return SendMessageResponse(
                success=True,
                message_id=None  # LINE API 不回傳 message_id
            )
            
        except LineBotApiError as e:
            logger.error(f"❌ 發送文字訊息失敗: {e}")
            return SendMessageResponse(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"❌ 發送文字訊息時發生未知錯誤: {e}")
            return SendMessageResponse(
                success=False,
                error_message=f"未知錯誤: {str(e)}"
            )
    
    async def send_image_message(
        self, 
        user_id: str, 
        original_content_url: str, 
        preview_image_url: str
    ) -> SendMessageResponse:
        """發送圖片訊息
        
        Args:
            user_id: 目標使用者 ID
            original_content_url: 原始圖片網址
            preview_image_url: 預覽圖片網址
            
        Returns:
            SendMessageResponse: 發送結果
        """
        try:
            message = ImageSendMessage(
                original_content_url=original_content_url,
                preview_image_url=preview_image_url
            )
            self.line_bot_api.push_message(user_id, message)
            
            logger.info(f"✅ 成功發送圖片訊息到使用者 {user_id}")
            return SendMessageResponse(
                success=True,
                message_id=None
            )
            
        except LineBotApiError as e:
            logger.error(f"❌ 發送圖片訊息失敗: {e}")
            return SendMessageResponse(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"❌ 發送圖片訊息時發生未知錯誤: {e}")
            return SendMessageResponse(
                success=False,
                error_message=f"未知錯誤: {str(e)}"
            )
    
    async def reply_message(self, reply_token: str, text: str) -> SendMessageResponse:
        """回覆訊息
        
        Args:
            reply_token: 回覆 token
            text: 回覆訊息內容
            
        Returns:
            SendMessageResponse: 發送結果
        """
        try:
            message = TextSendMessage(text=text)
            self.line_bot_api.reply_message(reply_token, message)
            
            logger.info(f"✅ 成功回覆訊息")
            return SendMessageResponse(
                success=True,
                message_id=None
            )
            
        except LineBotApiError as e:
            logger.error(f"❌ 回覆訊息失敗: {e}")
            return SendMessageResponse(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"❌ 回覆訊息時發生未知錯誤: {e}")
            return SendMessageResponse(
                success=False,
                error_message=f"未知錯誤: {str(e)}"
            )
    
    async def get_user_profile(self, user_id: str) -> Optional[User]:
        """取得使用者資料
        
        Args:
            user_id: 使用者 ID
            
        Returns:
            Optional[User]: 使用者物件，失敗時回傳 None
        """
        try:
            profile = self.line_bot_api.get_profile(user_id)
            
            return User(
                user_id=user_id,
                display_name=profile.display_name,
                picture_url=profile.picture_url,
                status_message=profile.status_message,
                language=getattr(profile, 'language', None)
            )
            
        except LineBotApiError as e:
            logger.error(f"❌ 取得使用者資料失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 取得使用者資料時發生未知錯誤: {e}")
            return None
    
    async def get_message_content(self, message_id: str) -> Optional[bytes]:
        """取得訊息內容 (主要用於圖片、語音等)
        
        Args:
            message_id: 訊息 ID
            
        Returns:
            Optional[bytes]: 訊息內容的二進位資料，失敗時回傳 None
        """
        try:
            message_content = self.line_bot_api.get_message_content(message_id)
            
            # 讀取所有內容到記憶體中
            content = b''
            for chunk in message_content.iter_content():
                content += chunk
            
            logger.info(f"✅ 成功取得訊息內容，大小: {len(content)} bytes")
            return content
            
        except LineBotApiError as e:
            logger.error(f"❌ 取得訊息內容失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 取得訊息內容時發生未知錯誤: {e}")
            return None


class MessageConverter:
    """訊息轉換器 - 將 LINE SDK 訊息轉換為領域模型"""
    
    @staticmethod
    def from_line_message(event: MessageEvent) -> Optional[BaseMessage]:
        """將 LINE 訊息事件轉換為領域模型
        
        Args:
            event: LINE 訊息事件
            
        Returns:
            Optional[BaseMessage]: 轉換後的領域模型，不支援的類型回傳 None
        """
        try:
            base_data = {
                "message_id": event.message.id,
                "user_id": event.source.user_id,
                "raw_data": event.as_dict()
            }
            
            # 文字訊息
            if isinstance(event.message, LineTextMessage):
                return TextMessage(
                    text=event.message.text,
                    **base_data
                )
            
            # 圖片訊息
            elif isinstance(event.message, LineImageMessage):
                return ImageMessage(
                    content_type=getattr(event.message, 'content_provider', {}).get('type'),
                    **base_data
                )
            
            # 其他類型暫不支援，但可以擴展
            else:
                logger.warning(f"⚠️ 不支援的訊息類型: {type(event.message)}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 轉換訊息時發生錯誤: {e}")
            return None