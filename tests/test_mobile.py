"""
Mobile app support tests - Task 19: Comprehensive Testing Suite
Tests for: GET /api/mobile/offline-data, POST /api/mobile/sync-data, GET /api/mobile/field-forms
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestMobileOfflineData:
    """Test mobile offline data endpoints"""
    
    def test_get_offline_data_success(self, auth_headers, test_user_id):
        """Test successful offline data retrieval"""
        response = client.get(f"/api/mobile/offline-data?userId={test_user_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "zones" in data["data"]
        assert "divisions" in data["data"]
        assert "stations" in data["data"]
        assert "fittingCategories" in data["data"]
        assert "fittingTypes" in data["data"]
    
    def test_get_offline_data_with_filters(self, auth_headers, test_user_id, test_zone_id):
        """Test offline data retrieval with filters"""
        response = client.get(
            f"/api/mobile/offline-data?userId={test_user_id}&zoneId={test_zone_id}&lastSyncTime=2025-01-01T00:00:00Z",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_offline_data_unauthorized(self):
        """Test offline data endpoint without authentication"""
        response = client.get("/api/mobile/offline-data?userId=test")
        assert response.status_code == 401

class TestMobileSync:
    """Test mobile sync endpoints"""
    
    def test_sync_data_success(self, auth_headers, test_user_id):
        """Test successful data sync"""
        sync_data = {
            "userId": test_user_id,
            "syncType": "full",
            "data": {
                "inspections": [
                    {
                        "qrCodeId": "test_qr_123",
                        "inspectionType": "routine",
                        "visualCondition": "good",
                        "checklistData": []
                    }
                ],
                "maintenanceRecords": [
                    {
                        "qrCodeId": "test_qr_123",
                        "maintenanceType": "preventive",
                        "workDescription": "Routine maintenance"
                    }
                ]
            }
        }
        
        response = client.post("/api/mobile/sync-data", json=sync_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "syncId" in data["data"]
        assert "status" in data["data"]
    
    def test_sync_data_invalid_user(self, auth_headers):
        """Test data sync with invalid user"""
        sync_data = {
            "userId": "invalid_user_id",
            "syncType": "full",
            "data": {}
        }
        
        response = client.post("/api/mobile/sync-data", json=sync_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_sync_data_unauthorized(self):
        """Test sync data endpoint without authentication"""
        response = client.post("/api/mobile/sync-data", json={})
        assert response.status_code == 401

class TestMobileFieldForms:
    """Test mobile field forms endpoints"""
    
    def test_get_field_forms_success(self, auth_headers):
        """Test successful field forms retrieval"""
        response = client.get("/api/mobile/field-forms", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "forms" in data["data"]
    
    def test_get_field_forms_by_type(self, auth_headers):
        """Test field forms retrieval by type"""
        response = client.get("/api/mobile/field-forms?formType=inspection", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_field_forms_unauthorized(self):
        """Test field forms endpoint without authentication"""
        response = client.get("/api/mobile/field-forms")
        assert response.status_code == 401
