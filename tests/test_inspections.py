"""
Inspection management tests - Task 19: Comprehensive Testing Suite
Tests for: GET/POST /api/inspections, PUT /api/inspections/:id/complete, GET /api/inspections/:id/photos/:photoIndex
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestInspectionManagement:
    """Test inspection management endpoints"""
    
    def test_get_inspections_success(self, auth_headers):
        """Test successful inspection listing"""
        response = client.get("/api/inspections", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "inspections" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_inspections_with_filters(self, auth_headers, test_qr_code_id):
        """Test inspection listing with filters"""
        response = client.get(
            f"/api/inspections?qrCodeId={test_qr_code_id}&inspectionType=routine&status=pending",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_create_inspection_success(self, auth_headers, test_qr_code_id):
        """Test successful inspection creation"""
        inspection_data = {
            "qrCodeId": test_qr_code_id,
            "inspectionType": "routine",
            "inspectionLocation": "Track Section A",
            "inspectionCoordinates": {
                "lat": 13.0827,
                "lng": 80.2707
            },
            "visualCondition": "good",
            "checklistData": [
                {
                    "item": "Visual condition check",
                    "status": "pass",
                    "value": 95,
                    "unit": "percentage"
                },
                {
                    "item": "Tightness check",
                    "status": "pass",
                    "value": 100,
                    "unit": "percentage"
                }
            ],
            "photos": ["base64_image_1", "base64_image_2"],
            "recommendation": "Continue monitoring",
            "weatherConditions": {
                "temperature": 25.5,
                "humidity": 60,
                "weather": "sunny"
            }
        }
        
        response = client.post("/api/inspections", json=inspection_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "inspection" in data["data"]
        assert data["data"]["inspection"]["inspectionType"] == inspection_data["inspectionType"]
    
    def test_create_inspection_invalid_qr_code(self, auth_headers):
        """Test inspection creation with invalid QR code"""
        inspection_data = {
            "qrCodeId": "invalid_qr_code_id",
            "inspectionType": "routine",
            "visualCondition": "good",
            "checklistData": []
        }
        
        response = client.post("/api/inspections", json=inspection_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_complete_inspection_success(self, auth_headers, test_inspection_id):
        """Test successful inspection completion"""
        completion_data = {
            "recommendation": "pass",
            "nextInspectionDue": "2025-12-15T00:00:00Z",
            "remarks": "All parameters within limits"
        }
        
        response = client.put(
            f"/api/inspections/{test_inspection_id}/complete",
            json=completion_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["inspection"]["recommendation"] == completion_data["recommendation"]
    
    def test_get_inspection_photo(self, auth_headers, test_inspection_id):
        """Test get inspection photo by index"""
        response = client.get(
            f"/api/inspections/{test_inspection_id}/photos/0",
            headers=auth_headers
        )
        
        # This would return binary image data
        assert response.status_code in [200, 404]  # 404 if no photos
    
    def test_get_inspection_by_id(self, auth_headers, test_inspection_id):
        """Test get inspection by ID"""
        response = client.get(f"/api/inspections/{test_inspection_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "inspection" in data["data"]
    
    def test_inspections_unauthorized(self):
        """Test inspection endpoints without authentication"""
        response = client.get("/api/inspections")
        assert response.status_code == 401
        
        response = client.post("/api/inspections", json={})
        assert response.status_code == 401
