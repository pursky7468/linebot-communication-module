"""訊息處理介面定義

定義外部模組需要實作的介面，實現業務邏輯委派
"""

from abc import ABC, abstractmethod
from typing import Optional, Union
from linebot_module.domain.models import (
    BaseMessage, TextMessage, ImageMessage, 
    AudioMessage, VideoMessage, LocationMessage, StickerMessage
)


class IMessageHandler(ABC):
    """訊息處理介面
    
    外部模組需要實作此介面來處理具體的業務邏輯
    """
    
    @abstractmethod
    async def handle_text_message(self, message: TextMessage) -> Optional[str]:
        """處理文字訊息
        
        Args:
            message: 文字訊息物件
            
        Returns:
            Optional[str]: 回應訊息內容，None 表示不回應
        """
        pass
    
    @abstractmethod
    async def handle_image_message(self, message: ImageMessage) -> Optional[str]:
        """處理圖片訊息
        
        Args:
            message: 圖片訊息物件
            
        Returns:
            Optional[str]: 回應訊息內容，None 表示不回應
        """
        pass
    
    async def handle_audio_message(self, message: AudioMessage) -> Optional[str]:
        """處理語音訊息 (預留擴展)
        
        Args:
            message: 語音訊息物件
            
        Returns:
            Optional[str]: 回應訊息內容，None 表示不回應
        """
        return None  # 預設實作：不處理
    
    async def handle_video_message(self, message: VideoMessage) -> Optional[str]:
        """處理影片訊息 (預留擴展)
        
        Args:
            message: 影片訊息物件
            
        Returns:
            Optional[str]: 回應訊息內容，None 表示不回應
        """
        return None  # 預設實作：不處理
    
    async def handle_location_message(self, message: LocationMessage) -> Optional[str]:
        """處理位置訊息 (預留擴展)
        
        Args:
            message: 位置訊息物件
            
        Returns:
            Optional[str]: 回應訊息內容，None 表示不回應
        """
        return None  # 預設實作：不處理
    
    async def handle_sticker_message(self, message: StickerMessage) -> Optional[str]:
        """處理貼圖訊息 (預留擴展)
        
        Args:
            message: 貼圖訊息物件
            
        Returns:
            Optional[str]: 回應訊息內容，None 表示不回應
        """
        return None  # 預設實作：不處理
    
    async def handle_unknown_message(self, message: BaseMessage) -> Optional[str]:
        """處理未知類型訊息
        
        Args:
            message: 基礎訊息物件
            
        Returns:
            Optional[str]: 回應訊息內容，None 表示不回應
        """
        return "抱歉，我無法處理此類型的訊息。"


class IUserService(ABC):
    """使用者服務介面
    
    定義使用者相關的業務邏輯介面
    """
    
    @abstractmethod
    async def get_user_info(self, user_id: str) -> Optional[dict]:
        """取得使用者資訊
        
        Args:
            user_id: 使用者 ID
            
        Returns:
            Optional[dict]: 使用者資訊，None 表示使用者不存在
        """
        pass
    
    @abstractmethod
    async def update_user_status(self, user_id: str, status: str) -> bool:
        """更新使用者狀態
        
        Args:
            user_id: 使用者 ID
            status: 新狀態
            
        Returns:
            bool: 更新是否成功
        """
        pass


class IMessageRouter(ABC):
    """訊息路由介面
    
    根據訊息類型路由到對應的處理器
    """
    
    @abstractmethod
    async def route_message(self, message: BaseMessage) -> Optional[str]:
        """路由訊息到對應的處理器
        
        Args:
            message: 訊息物件
            
        Returns:
            Optional[str]: 處理結果，None 表示不回應
        """
        pass