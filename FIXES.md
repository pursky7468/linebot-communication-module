# LINE BOT 通訊模組 - 修正記錄

## 🐛 **原始問題分析**

### **問題 1：埠號衝突**
- **現象**：服務無法啟動
- **原因**：埠號 8000 被其他服務佔用
- **解決**：將預設埠號改為 3000

### **問題 2：環境變數載入錯誤**
- **現象**：無法讀取 LINE BOT 設定
- **原因**：`pydantic-settings` 的 `env` 參數設定錯誤
- **解決**：修正 `settings.py` 中的 Field 定義，並加上 `python-dotenv` 支援

### **問題 3：訊息轉換失敗**
- **現象**：`'MessageEvent' object has no attribute 'as_dict'`
- **原因**：LINE Bot SDK 的 `MessageEvent` 物件沒有 `as_dict()` 方法
- **解決**：重新實作 `MessageConverter.from_line_message()` 方法

## 🔧 **具體修正內容**

### **1. 環境設定修正**

**檔案**: `linebot_module/config/settings.py`

**修正前**:
```python
line_channel_access_token: str = Field(
    ..., 
    env="Wq51IPI1JMJjqZPLPb8lANbLtGHIyFuRXepOAkG7mdivylAnL5JX2swGB3RTlN+dvo21xPsK9RvMrhV3nl1e6XgmNkQ3LDj4j3ZWicc3Ir2WO2+QYv9oX/Oh0ribId2rn7xX5+3y1dDCCnU8v6HCtwdB04t89/1O/w1cDnyilFU=",
    description="LINE Channel Access Token"
)
```

**修正後**:
```python
line_channel_access_token: str = Field(
    default="", 
    description="LINE Channel Access Token"
)
```

**修正說明**:
- 移除錯誤的 `env` 參數設定（將實際 token 值寫在程式碼中）
- 改用預設空值，讓 Pydantic 從環境變數自動讀取
- 加上 `python-dotenv` 手動載入確保相容性

### **2. 埠號設定修正**

**檔案**: `.env`

**修正前**:
```
PORT=8000
```

**修正後**:
```
PORT=3000
```

**修正說明**:
- 埠號 8000 被佔用，改為可用的 3000
- 與原有成功專案保持一致

### **3. 訊息轉換器修正**

**檔案**: `linebot_module/infrastructure/line_api_service.py`

**修正前**:
```python
def from_line_message(event: MessageEvent) -> Optional[BaseMessage]:
    try:
        base_data = {
            "message_id": event.message.id,
            "user_id": event.source.user_id,
            "raw_data": event.as_dict()  # ❌ 這個方法不存在
        }
```

**修正後**:
```python
def from_line_message(event: MessageEvent) -> Optional[BaseMessage]:
    try:
        # 修正：創建安全的原始資料字典
        raw_data = {
            "type": event.type,
            "mode": getattr(event, 'mode', None),
            "timestamp": getattr(event, 'timestamp', None),
            "source": {
                "type": event.source.type,
                "user_id": getattr(event.source, 'user_id', None)
            },
            "message": {
                "id": event.message.id,
                "type": event.message.type
            }
        }
        
        base_data = {
            "message_id": event.message.id,
            "user_id": event.source.user_id,
            "raw_data": raw_data
        }
```

**修正說明**:
- LINE Bot SDK 的 `MessageEvent` 物件沒有 `as_dict()` 方法
- 手動建立字典結構來保存原始事件資料
- 使用 `getattr()` 安全地存取可能不存在的屬性
- 加強錯誤處理和日誌記錄

## 📊 **測試驗證**

修正後通過以下測試：

1. ✅ **服務啟動測試**：成功在埠號 3000 啟動
2. ✅ **Webhook 連接測試**：LINE 平台成功連接
3. ✅ **訊息接收測試**：成功接收使用者訊息
4. ✅ **訊息轉換測試**：正確轉換為領域模型
5. ✅ **訊息回應測試**：成功回覆使用者

## 🎯 **最終狀態**

- **埠號**：3000 (可用)
- **環境變數**：正確載入
- **訊息轉換**：正常運作
- **收發功能**：完全正常

## 💡 **經驗學習**

1. **埠號管理**：開發前先檢查埠號可用性
2. **環境變數設定**：Pydantic Settings 的 `env` 參數不是用來設定預設值
3. **API 相容性**：不同版本的 SDK 可能有方法差異，需要查閱文檔
4. **錯誤診斷**：建立診斷工具有助於快速定位問題