"""領域模型定義

定義 LINE BOT 通訊模組的核心領域模型
包含訊息、使用者等基本實體
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """訊息類型列舉"""
    TEXT = "text"          # 文字訊息
    IMAGE = "image"        # 圖片訊息
    AUDIO = "audio"        # 語音訊息
    VIDEO = "video"        # 影片訊息
    FILE = "file"          # 檔案訊息
    LOCATION = "location"  # 位置訊息
    STICKER = "sticker"    # 貼圖訊息


class BaseMessage(BaseModel, ABC):
    """訊息基底類別"""
    
    message_id: str = Field(..., description="訊息唯一識別碼")
    user_id: str = Field(..., description="使用者 ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="訊息時間戳記")
    message_type: MessageType = Field(..., description="訊息類型")
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="原始訊息資料")
    
    class Config:
        """Pydantic 設定"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TextMessage(BaseMessage):
    """文字訊息模型"""
    
    message_type: MessageType = Field(default=MessageType.TEXT, description="訊息類型")
    text: str = Field(..., min_length=1, max_length=5000, description="訊息文字內容")
    
    def __str__(self) -> str:
        return f"TextMessage(user_id={self.user_id}, text='{self.text[:50]}...')"


class ImageMessage(BaseMessage):
    """圖片訊息模型"""
    
    message_type: MessageType = Field(default=MessageType.IMAGE, description="訊息類型")
    image_url: Optional[str] = Field(default=None, description="圖片網址")
    preview_url: Optional[str] = Field(default=None, description="預覽圖片網址")
    file_size: Optional[int] = Field(default=None, ge=0, description="檔案大小 (bytes)")
    content_type: Optional[str] = Field(default=None, description="內容類型 (MIME type)")
    
    def __str__(self) -> str:
        return f"ImageMessage(user_id={self.user_id}, image_url={self.image_url})"


class AudioMessage(BaseMessage):
    """語音訊息模型 (預留擴展)"""
    
    message_type: MessageType = Field(default=MessageType.AUDIO, description="訊息類型")
    audio_url: Optional[str] = Field(default=None, description="語音檔案網址")
    duration: Optional[int] = Field(default=None, ge=0, description="語音長度 (毫秒)")
    
    def __str__(self) -> str:
        return f"AudioMessage(user_id={self.user_id}, duration={self.duration}ms)"


class VideoMessage(BaseMessage):
    """影片訊息模型 (預留擴展)"""
    
    message_type: MessageType = Field(default=MessageType.VIDEO, description="訊息類型")
    video_url: Optional[str] = Field(default=None, description="影片檔案網址")
    preview_url: Optional[str] = Field(default=None, description="預覽圖片網址")
    duration: Optional[int] = Field(default=None, ge=0, description="影片長度 (毫秒)")
    
    def __str__(self) -> str:
        return f"VideoMessage(user_id={self.user_id}, duration={self.duration}ms)"


class LocationMessage(BaseMessage):
    """位置訊息模型 (預留擴展)"""
    
    message_type: MessageType = Field(default=MessageType.LOCATION, description="訊息類型")
    title: Optional[str] = Field(default=None, description="位置標題")
    address: Optional[str] = Field(default=None, description="位置地址")
    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="緯度")
    longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="經度")
    
    def __str__(self) -> str:
        return f"LocationMessage(user_id={self.user_id}, title='{self.title}')"


class StickerMessage(BaseMessage):
    """貼圖訊息模型 (預留擴展)"""
    
    message_type: MessageType = Field(default=MessageType.STICKER, description="訊息類型")
    package_id: Optional[str] = Field(default=None, description="貼圖包 ID")
    sticker_id: Optional[str] = Field(default=None, description="貼圖 ID")
    
    def __str__(self) -> str:
        return f"StickerMessage(user_id={self.user_id}, package_id={self.package_id}, sticker_id={self.sticker_id})"


class User(BaseModel):
    """使用者模型"""
    
    user_id: str = Field(..., description="使用者唯一識別碼")
    display_name: Optional[str] = Field(default=None, description="顯示名稱")
    picture_url: Optional[str] = Field(default=None, description="大頭貼網址")
    status_message: Optional[str] = Field(default=None, description="狀態訊息")
    language: Optional[str] = Field(default=None, description="語言設定")
    
    def __str__(self) -> str:
        return f"User(user_id={self.user_id}, display_name='{self.display_name}')"


class SendMessageRequest(BaseModel):
    """發送訊息請求模型"""
    
    user_id: str = Field(..., description="目標使用者 ID")
    message_type: MessageType = Field(..., description="訊息類型")
    content: str = Field(..., description="訊息內容")
    quick_reply: Optional[Dict[str, Any]] = Field(default=None, description="快速回覆選項")
    
    class Config:
        """Pydantic 設定"""
        use_enum_values = True


class SendMessageResponse(BaseModel):
    """發送訊息回應模型"""
    
    success: bool = Field(..., description="發送是否成功")
    message_id: Optional[str] = Field(default=None, description="訊息 ID")
    error_message: Optional[str] = Field(default=None, description="錯誤訊息")
    timestamp: datetime = Field(default_factory=datetime.now, description="回應時間戳記")
    
    class Config:
        """Pydantic 設定"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }