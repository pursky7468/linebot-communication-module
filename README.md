# LINE BOT 通訊模組

基於 Clean Architecture 設計的 LINE BOT 通訊模組，專門負責與 LINE 平台的訊息收發功能。

## 🏗️ 架構設計

本模組採用分層架構設計，遵循 SOLID 原則：

```
📁 linebot_module/
├── 🔧 application/     # 應用層 - FastAPI 端點與路由
├── 🎯 domain/          # 領域層 - 訊息模型與業務介面
├── 🔌 infrastructure/  # 基礎設施層 - LINE SDK 實作
├── 📡 interfaces/      # 介面層 - 外部模組委派介面
└── ⚙️ config/         # 設定管理
```

## ✨ 功能特色

- ✅ **訊息接收**：支援文字、圖片訊息（可擴展其他類型）
- ✅ **訊息發送**：回應式訊息發送功能
- ✅ **委派機制**：將業務邏輯委派給外部模組處理
- ✅ **型別安全**：完整的 Python 型別提示
- ✅ **自動文檔**：FastAPI 自動生成 API 文檔
- ✅ **依賴注入**：內建 DI 系統，易於測試
- ✅ **擴展性**：預留支援其他訊息類型的架構

## 🚀 快速開始

### 1. 環境準備

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境 (Windows)
venv\Scripts\activate

# 啟動虛擬環境 (macOS/Linux)
source venv/bin/activate

# 安裝依賴套件
pip install -r requirements.txt
```

### 2. 環境設定

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，填入您的 LINE BOT 設定
```

### 3. 啟動服務

```bash
# 啟動 FastAPI 服務
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. ngrok 設定 (開發用)

```bash
# 啟動 ngrok
ngrok http 8000

# 將產生的 URL 設定到 LINE Developers Console
```

## 📖 API 文檔

啟動服務後，可透過以下網址查看自動生成的 API 文檔：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 測試

```bash
# 執行所有測試
pytest

# 執行測試並產生覆蓋率報告
pytest --cov=linebot_module --cov-report=html

# 執行型別檢查
mypy linebot_module/

# 執行程式碼格式化
black linebot_module/

# 執行程式碼風格檢查
flake8 linebot_module/
```

## 📞 使用方式

### 基本使用

```python
from linebot_module.interfaces.message_handler import IMessageHandler
from linebot_module.domain.models import TextMessage, ImageMessage

# 實作訊息處理介面
class MyMessageHandler(IMessageHandler):
    async def handle_text_message(self, message: TextMessage) -> str:
        # 處理文字訊息的業務邏輯
        return f"收到訊息：{message.text}"
    
    async def handle_image_message(self, message: ImageMessage) -> str:
        # 處理圖片訊息的業務邏輯
        return "收到圖片訊息"

# 註冊訊息處理器
app.dependency_overrides[IMessageHandler] = lambda: MyMessageHandler()
```

## 🔧 技術棧

- **Web 框架**: FastAPI
- **LINE SDK**: line-bot-sdk-python
- **資料驗證**: Pydantic
- **測試框架**: pytest
- **程式碼品質**: black, flake8, mypy

## 📄 授權

MIT License

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

---

**注意**: 此模組專門負責 LINE 平台通訊，業務邏輯請實作在外部模組中。