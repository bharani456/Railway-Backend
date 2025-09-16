"""
QR code management tests - Task 19: Comprehensive Testing Suite
Tests for: POST /api/qr-codes/generate-batch, GET /api/qr-codes/:qrCode, 
          POST /api/qr-codes/:qrCode/scan, PUT /api/qr-codes/:id/verify
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestQRCodeManagement:
    """Test QR code management endpoints"""
    
    def test_generate_batch_qr_codes_success(self, auth_headers, test_batch_id):
        """Test successful QR code batch generation"""
        batch_data = {
            "fittingBatchId": test_batch_id,
            "quantity": 10,
            "markingMachineId": "LASER-001",
            "markingOperatorId": "operator123"
        }
        
        response = client.post("/api/qr-codes/generate-batch", json=batch_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "qrCodes" in data["data"]
        assert "batchSummary" in data["data"]
        assert len(data["data"]["qrCodes"]) == 10
    
    def test_generate_batch_qr_codes_invalid_batch(self, auth_headers):
        """Test QR code generation with invalid batch ID"""
        batch_data = {
            "fittingBatchId": "invalid_batch_id",
            "quantity": 10,
            "markingMachineId": "LASER-001",
            "markingOperatorId": "operator123"
        }
        
        response = client.post("/api/qr-codes/generate-batch", json=batch_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_generate_batch_qr_codes_invalid_quantity(self, auth_headers, test_batch_id):
        """Test QR code generation with invalid quantity"""
        batch_data = {
            "fittingBatchId": test_batch_id,
            "quantity": 0,
            "markingMachineId": "LASER-001",
            "markingOperatorId": "operator123"
        }
        
        response = client.post("/api/qr-codes/generate-batch", json=batch_data, headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_get_qr_code_details_success(self, auth_headers, test_qr_code):
        """Test successful QR code details retrieval"""
        response = client.get(f"/api/qr-codes/{test_qr_code}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "qrCode" in data["data"]
        assert data["data"]["qrCode"]["qrCode"] == test_qr_code
    
    def test_get_qr_code_details_not_found(self, auth_headers):
        """Test QR code details retrieval with non-existent QR code"""
        response = client.get("/api/qr-codes/INVALID_QR_CODE", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_scan_qr_code_success(self, auth_headers, test_qr_code):
        """Test successful QR code scanning"""
        scan_data = {
            "scanLocation": "Track Section A",
            "scanCoordinates": {"lat": 13.0827, "lng": 80.2707},
            "scanPurpose": "inspection",
            "deviceInfo": {"type": "mobile", "os": "Android"}
        }
        
        response = client.post(f"/api/qr-codes/{test_qr_code}/scan", json=scan_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "scanLog" in data["data"]
    
    def test_scan_qr_code_invalid_qr(self, auth_headers):
        """Test QR code scanning with invalid QR code"""
        scan_data = {
            "scanLocation": "Track Section A",
            "scanCoordinates": {"lat": 13.0827, "lng": 80.2707},
            "scanPurpose": "inspection"
        }
        
        response = client.post("/api/qr-codes/INVALID_QR/scan", json=scan_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_verify_qr_code_success(self, auth_headers, test_qr_code_id):
        """Test successful QR code verification"""
        verify_data = {
            "verificationStatus": "verified",
            "printQualityScore": 0.95
        }
        
        response = client.put(f"/api/qr-codes/{test_qr_code_id}/verify", json=verify_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "qrCode" in data["data"]
    
    def test_verify_qr_code_invalid_id(self, auth_headers):
        """Test QR code verification with invalid ID"""
        verify_data = {
            "verificationStatus": "verified",
            "printQualityScore": 0.95
        }
        
        response = client.put("/api/qr-codes/invalid_id/verify", json=verify_data, headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_get_qr_codes_list(self, auth_headers):
        """Test QR codes listing"""
        response = client.get("/api/qr-codes", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "qrCodes" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_qr_codes_with_filters(self, auth_headers):
        """Test QR codes listing with filters"""
        response = client.get(
            "/api/qr-codes?status=generated&page=1&limit=5",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_qr_code_unauthorized(self):
        """Test QR code endpoints without authentication"""
        response = client.get("/api/qr-codes")
        assert response.status_code == 401
        
        response = client.post("/api/qr-codes/generate-batch", json={})
        assert response.status_code == 401
