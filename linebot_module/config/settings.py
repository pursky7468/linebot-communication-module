"""應用程式設定管理

使用 Pydantic Settings 管理環境變數和設定
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """應用程式設定類別"""
    
    # LINE BOT 設定
    line_channel_access_token: str = Field(
        default="", 
        description="LINE Channel Access Token"
    )
    
    line_channel_secret: str = Field(
        default="", 
        description="LINE Channel Secret"
    )
    
    # 伺服器設定
    host: str = Field(
        default="0.0.0.0", 
        description="伺服器主機位址"
    )
    
    port: int = Field(
        default=8000, 
        description="伺服器連接埠"
    )
    
    debug: bool = Field(
        default=True, 
        description="偵錯模式"
    )
    
    # ngrok 設定 (開發用)
    ngrok_url: Optional[str] = Field(
        default=None, 
        description="ngrok 外部網址"
    )
    
    # 日誌設定
    log_level: str = Field(
        default="INFO", 
        description="日誌等級"
    )
    
    class Config:
        """設定"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 手動載入環境變數以確保相容性
from dotenv import load_dotenv
load_dotenv()

# 全域設定實例
settings = Settings()