"""
Installation management tests - Task 19: Comprehensive Testing Suite
Tests for: POST /api/installations, GET /api/installations, PUT /api/installations/:id/status
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestInstallationManagement:
    """Test installation management endpoints"""
    
    def test_create_installation_success(self, auth_headers, test_qr_code_id, test_zone_id):
        """Test successful installation creation"""
        installation_data = {
            "qrCodeId": test_qr_code_id,
            "zoneId": test_zone_id,
            "trackSection": "Section A-1",
            "kilometerPost": "KM 10.5",
            "installationCoordinates": {"lat": 13.0827, "lng": 80.2707}
        }
        
        response = client.post("/api/installations", json=installation_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "installation" in data["data"]
        assert data["data"]["installation"]["trackSection"] == installation_data["trackSection"]
    
    def test_create_installation_invalid_qr_code(self, auth_headers, test_zone_id):
        """Test installation creation with invalid QR code"""
        installation_data = {
            "qrCodeId": "invalid_qr_code_id",
            "zoneId": test_zone_id,
            "trackSection": "Section A-1",
            "kilometerPost": "KM 10.5",
            "installationCoordinates": {"lat": 13.0827, "lng": 80.2707}
        }
        
        response = client.post("/api/installations", json=installation_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_create_installation_invalid_coordinates(self, auth_headers, test_qr_code_id, test_zone_id):
        """Test installation creation with invalid coordinates"""
        installation_data = {
            "qrCodeId": test_qr_code_id,
            "zoneId": test_zone_id,
            "trackSection": "Section A-1",
            "kilometerPost": "KM 10.5",
            "installationCoordinates": {"lat": 200, "lng": 200}  # Invalid coordinates
        }
        
        response = client.post("/api/installations", json=installation_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_get_installations_success(self, auth_headers):
        """Test successful installations listing"""
        response = client.get("/api/installations", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "installations" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_installations_with_filters(self, auth_headers, test_zone_id):
        """Test installations listing with filters"""
        response = client.get(
            f"/api/installations?zoneId={test_zone_id}&status=installed&page=1&limit=5",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_installations_by_track_section(self, auth_headers):
        """Test installations listing by track section"""
        response = client.get(
            "/api/installations?trackSection=Section A-1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_update_installation_status_success(self, auth_headers, test_installation_id):
        """Test successful installation status update"""
        status_data = {
            "status": "maintenance_due",
            "remarks": "Routine maintenance required"
        }
        
        response = client.put(f"/api/installations/{test_installation_id}/status", json=status_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["installation"]["status"] == status_data["status"]
    
    def test_update_installation_status_invalid_id(self, auth_headers):
        """Test installation status update with invalid ID"""
        status_data = {
            "status": "maintenance_due",
            "remarks": "Routine maintenance required"
        }
        
        response = client.put("/api/installations/invalid_id/status", json=status_data, headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_get_installation_by_id(self, auth_headers, test_installation_id):
        """Test get installation by ID"""
        response = client.get(f"/api/installations/{test_installation_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "installation" in data["data"]
    
    def test_get_installation_not_found(self, auth_headers):
        """Test get installation with non-existent ID"""
        response = client.get("/api/installations/507f1f77bcf86cd799439011", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_installations_unauthorized(self):
        """Test installation endpoints without authentication"""
        response = client.get("/api/installations")
        assert response.status_code == 401
        
        response = client.post("/api/installations", json={})
        assert response.status_code == 401
    
    def test_installation_statistics(self, auth_headers):
        """Test installation statistics"""
        response = client.get("/api/installations/statistics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "statistics" in data["data"]
    
    def test_installations_by_location(self, auth_headers):
        """Test installations by location"""
        response = client.get(
            "/api/installations/by-location?lat=13.0827&lng=80.2707&radius=1000",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "installations" in data["data"]
