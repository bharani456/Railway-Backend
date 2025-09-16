"""
Maintenance management tests - Task 19: Comprehensive Testing Suite
Tests for: GET/POST /api/maintenance-records, PUT /api/maintenance-records/:id/quality-check
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestMaintenanceManagement:
    """Test maintenance record management endpoints"""
    
    def test_get_maintenance_records_success(self, auth_headers):
        """Test successful maintenance record listing"""
        response = client.get("/api/maintenance-records", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "maintenanceRecords" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_maintenance_records_with_filters(self, auth_headers, test_qr_code_id):
        """Test maintenance record listing with filters"""
        response = client.get(
            f"/api/maintenance-records?qrCodeId={test_qr_code_id}&maintenanceType=corrective&status=completed",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_create_maintenance_record_success(self, auth_headers, test_qr_code_id):
        """Test successful maintenance record creation"""
        maintenance_data = {
            "qrCodeId": test_qr_code_id,
            "maintenanceType": "corrective",
            "workDescription": "Replaced worn rail clip",
            "partsReplaced": [
                {
                    "part": "rail_clip",
                    "quantity": 1,
                    "cost": 50.00
                }
            ],
            "partsUsed": [
                {
                    "part": "replacement_clip",
                    "quantity": 1,
                    "cost": 45.00
                }
            ],
            "cost": 100.00,
            "beforePhotos": ["base64_image_1"],
            "afterPhotos": ["base64_image_2"],
            "workOrderNumber": "WO-2025-001"
        }
        
        response = client.post("/api/maintenance-records", json=maintenance_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "maintenanceRecord" in data["data"]
        assert data["data"]["maintenanceRecord"]["maintenanceType"] == maintenance_data["maintenanceType"]
    
    def test_create_maintenance_record_invalid_qr_code(self, auth_headers):
        """Test maintenance record creation with invalid QR code"""
        maintenance_data = {
            "qrCodeId": "invalid_qr_code_id",
            "maintenanceType": "corrective",
            "workDescription": "Test maintenance"
        }
        
        response = client.post("/api/maintenance-records", json=maintenance_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_maintenance_record_quality_check(self, auth_headers, test_maintenance_record_id):
        """Test maintenance record quality check update"""
        quality_check_data = {
            "qualityCheckPassed": True,
            "nextMaintenanceDue": "2026-03-15T00:00:00Z",
            "remarks": "Quality check passed successfully"
        }
        
        response = client.put(
            f"/api/maintenance-records/{test_maintenance_record_id}/quality-check",
            json=quality_check_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["maintenanceRecord"]["qualityCheckPassed"] == quality_check_data["qualityCheckPassed"]
    
    def test_get_maintenance_record_by_id(self, auth_headers, test_maintenance_record_id):
        """Test get maintenance record by ID"""
        response = client.get(f"/api/maintenance-records/{test_maintenance_record_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "maintenanceRecord" in data["data"]
    
    def test_maintenance_records_unauthorized(self):
        """Test maintenance record endpoints without authentication"""
        response = client.get("/api/maintenance-records")
        assert response.status_code == 401
        
        response = client.post("/api/maintenance-records", json={})
        assert response.status_code == 401
