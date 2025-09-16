"""
Notification and search tests - Task 19: Comprehensive Testing Suite
Tests for: GET /api/notifications, POST /api/notifications/mark-read, GET /api/search
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestNotifications:
    """Test notification endpoints"""
    
    def test_get_notifications_success(self, auth_headers, test_user_id):
        """Test successful notifications retrieval"""
        response = client.get(f"/api/notifications?userId={test_user_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "notifications" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_notifications_with_filters(self, auth_headers, test_user_id):
        """Test notifications retrieval with filters"""
        response = client.get(
            f"/api/notifications?userId={test_user_id}&type=alert&isRead=false&priority=high",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_mark_notifications_read_success(self, auth_headers, test_user_id):
        """Test successful mark notifications as read"""
        mark_read_data = {
            "notificationIds": ["notif_1", "notif_2"],
            "markAllAsRead": False
        }
        
        response = client.post(
            "/api/notifications/mark-read",
            json=mark_read_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "updatedCount" in data["data"]
    
    def test_mark_all_notifications_read(self, auth_headers, test_user_id):
        """Test mark all notifications as read"""
        mark_read_data = {
            "userId": test_user_id,
            "markAllAsRead": True
        }
        
        response = client.post(
            "/api/notifications/mark-read",
            json=mark_read_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_notifications_unauthorized(self):
        """Test notification endpoints without authentication"""
        response = client.get("/api/notifications?userId=test")
        assert response.status_code == 401
        
        response = client.post("/api/notifications/mark-read", json={})
        assert response.status_code == 401

class TestSearch:
    """Test search endpoints"""
    
    def test_search_success(self, auth_headers):
        """Test successful search"""
        response = client.get("/api/search?q=rail&type=all", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "results" in data["data"]
        assert "totalResults" in data["data"]
    
    def test_search_by_type(self, auth_headers):
        """Test search by specific type"""
        response = client.get("/api/search?q=test&type=fitting&limit=10", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_search_with_filters(self, auth_headers, test_zone_id):
        """Test search with filters"""
        response = client.get(
            f"/api/search?q=clip&type=fitting&zoneId={test_zone_id}&status=active",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_search_empty_query(self, auth_headers):
        """Test search with empty query"""
        response = client.get("/api/search?q=", headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_search_unauthorized(self):
        """Test search endpoint without authentication"""
        response = client.get("/api/search?q=test")
        assert response.status_code == 401
