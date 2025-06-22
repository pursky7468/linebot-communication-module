"""測試 API 端點"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


class TestWebhookEndpoint:
    """測試 Webhook 端點"""
    
    def test_webhook_invalid_signature(self, client):
        """測試無效簽章"""
        response = client.post(
            "/api/v1/webhook",
            json={"events": []},
            headers={"X-Line-Signature": "invalid_signature"}
        )
        
        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]
    
    def test_webhook_missing_signature(self, client):
        """測試缺少簽章"""
        response = client.post(
            "/api/v1/webhook",
            json={"events": []}
        )
        
        assert response.status_code == 400


class TestSendMessageEndpoint:
    """測試發送訊息端點"""
    
    @patch('linebot_module.infrastructure.line_api_service.LineApiService.send_text_message')
    def test_send_text_message_success(self, mock_send, client):
        """測試成功發送文字訊息"""
        # 設定模擬回應
        from linebot_module.domain.models import SendMessageResponse
        mock_send.return_value = SendMessageResponse(success=True)
        
        response = client.post(
            "/api/v1/send-message",
            json={
                "user_id": "user_001",
                "message_type": "text",
                "content": "Hello, World!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_send_message_invalid_type(self, client):
        """測試發送不支援的訊息類型"""
        response = client.post(
            "/api/v1/send-message",
            json={
                "user_id": "user_001",
                "message_type": "unsupported",
                "content": "Hello!"
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestUserProfileEndpoint:
    """測試使用者資料端點"""
    
    @patch('linebot_module.infrastructure.line_api_service.LineApiService.get_user_profile')
    def test_get_user_profile_success(self, mock_get_profile, client):
        """測試成功取得使用者資料"""
        # 設定模擬回應
        from linebot_module.domain.models import User
        mock_user = User(
            user_id="user_001",
            display_name="Test User",
            picture_url="https://example.com/avatar.jpg"
        )
        mock_get_profile.return_value = mock_user
        
        response = client.get("/api/v1/user/user_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user_001"
        assert data["display_name"] == "Test User"
    
    @patch('linebot_module.infrastructure.line_api_service.LineApiService.get_user_profile')
    def test_get_user_profile_not_found(self, mock_get_profile, client):
        """測試使用者不存在"""
        mock_get_profile.return_value = None
        
        response = client.get("/api/v1/user/nonexistent")
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


class TestHealthCheckEndpoint:
    """測試健康檢查端點"""
    
    def test_health_check(self, client):
        """測試健康檢查"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "linebot-communication-module"
        assert data["version"] == "1.0.0"
    
    def test_root_endpoint(self, client):
        """測試根端點"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"