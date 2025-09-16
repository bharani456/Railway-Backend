"""
Integration tests - Task 19: Comprehensive Testing Suite
Tests for: GET /api/integrations/udm/status, POST /api/integrations/udm/sync, GET /api/integrations/tms/status
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestUDMIntegration:
    """Test UDM portal integration endpoints"""
    
    def test_get_udm_status_success(self, auth_headers):
        """Test successful UDM status retrieval"""
        response = client.get("/api/integrations/udm/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "isConnected" in data["data"]
        assert "lastSyncTime" in data["data"]
        assert "syncStatus" in data["data"]
    
    def test_udm_sync_success(self, auth_headers):
        """Test successful UDM sync"""
        sync_data = {
            "syncType": "full",
            "dateRange": {
                "start": "2025-01-01",
                "end": "2025-01-31"
            }
        }
        
        response = client.post("/api/integrations/udm/sync", json=sync_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "syncId" in data["data"]
        assert "status" in data["data"]
    
    def test_udm_sync_invalid_date_range(self, auth_headers):
        """Test UDM sync with invalid date range"""
        sync_data = {
            "syncType": "full",
            "dateRange": {
                "start": "2025-01-31",
                "end": "2025-01-01"  # Invalid: end before start
            }
        }
        
        response = client.post("/api/integrations/udm/sync", json=sync_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_udm_unauthorized(self):
        """Test UDM integration endpoints without authentication"""
        response = client.get("/api/integrations/udm/status")
        assert response.status_code == 401
        
        response = client.post("/api/integrations/udm/sync", json={})
        assert response.status_code == 401

class TestTMSIntegration:
    """Test TMS portal integration endpoints"""
    
    def test_get_tms_status_success(self, auth_headers):
        """Test successful TMS status retrieval"""
        response = client.get("/api/integrations/tms/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "isConnected" in data["data"]
        assert "lastSyncTime" in data["data"]
        assert "syncStatus" in data["data"]
    
    def test_tms_sync_success(self, auth_headers):
        """Test successful TMS sync"""
        sync_data = {
            "syncType": "incremental",
            "lastSyncTime": "2025-01-01T00:00:00Z"
        }
        
        response = client.post("/api/integrations/tms/sync", json=sync_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "syncId" in data["data"]
        assert "status" in data["data"]
    
    def test_tms_unauthorized(self):
        """Test TMS integration endpoints without authentication"""
        response = client.get("/api/integrations/tms/status")
        assert response.status_code == 401
        
        response = client.post("/api/integrations/tms/sync", json={})
        assert response.status_code == 401
