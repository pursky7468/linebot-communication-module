"""使用範例：如何使用 LINE BOT 通訊模組

這個範例展示如何實作自己的訊息處理器並整合到 LINE BOT 模組中
"""

from linebot_module.interfaces.message_handler import IMessageHandler
from linebot_module.domain.models import TextMessage, ImageMessage
from main import app


class CustomMessageHandler(IMessageHandler):
    """自訂訊息處理器範例"""
    
    async def handle_text_message(self, message: TextMessage) -> str:
        """處理文字訊息的業務邏輯"""
        text = message.text.lower()
        
        # 簡單的關鍵字回應
        if "hello" in text or "hi" in text:
            return f"Hello! 很高興見到您，{message.user_id}！"
        
        elif "help" in text:
            return "我可以回應以下指令：\n- hello/hi: 打招呼\n- help: 顯示說明\n- echo: 重複您的訊息"
        
        elif text.startswith("echo "):
            return f"您說：{text[5:]}"
        
        else:
            return f"收到您的訊息：{message.text}\n輸入 'help' 查看可用指令"
    
    async def handle_image_message(self, message: ImageMessage) -> str:
        """處理圖片訊息的業務邏輯"""
        # 在實際應用中，您可能會：
        # 1. 下載圖片內容
        # 2. 進行圖片分析（OCR、物件識別等）
        # 3. 儲存圖片到雲端儲存
        
        return "感謝您分享圖片！我已經收到了。"


# 註冊自訂的訊息處理器
app.dependency_overrides[IMessageHandler] = lambda: CustomMessageHandler()


if __name__ == "__main__":
    import uvicorn
    from linebot_module.config.settings import settings
    
    print("🚀 啟動自訂 LINE BOT...")
    print("📝 使用自訂訊息處理器")
    print(f"🌐 服務將運行在: http://{settings.host}:{settings.port}")
    print(f"📖 API 文檔: http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        "example_usage:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )