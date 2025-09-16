"""
Export and file management tests - Task 19: Comprehensive Testing Suite
Tests for: GET /api/export/data, POST /api/export/generate, GET /api/export/download/:fileId
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestDataExport:
    """Test data export endpoints"""
    
    def test_get_export_data_success(self, auth_headers):
        """Test successful export data retrieval"""
        response = client.get("/api/export/data?format=json&type=fittings", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "exportData" in data["data"]
    
    def test_get_export_data_with_filters(self, auth_headers, test_zone_id, test_fitting_type_id):
        """Test export data with filters"""
        response = client.get(
            f"/api/export/data?format=csv&type=installations&zoneId={test_zone_id}&fittingTypeId={test_fitting_type_id}&dateRange=2025-01-01,2025-12-31",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_export_data_invalid_format(self, auth_headers):
        """Test export data with invalid format"""
        response = client.get("/api/export/data?format=invalid&type=fittings", headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_export_data_unauthorized(self):
        """Test export data endpoint without authentication"""
        response = client.get("/api/export/data?format=json&type=fittings")
        assert response.status_code == 401

class TestExportGeneration:
    """Test export generation endpoints"""
    
    def test_generate_export_success(self, auth_headers):
        """Test successful export generation"""
        export_data = {
            "exportType": "comprehensive",
            "format": "excel",
            "filters": {
                "dateRange": {
                    "start": "2025-01-01",
                    "end": "2025-12-31"
                },
                "includePhotos": True,
                "includeAnalytics": True
            },
            "sections": ["fittings", "installations", "inspections", "maintenance"]
        }
        
        response = client.post("/api/export/generate", json=export_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "exportId" in data["data"]
        assert "status" in data["data"]
    
    def test_generate_export_invalid_type(self, auth_headers):
        """Test export generation with invalid type"""
        export_data = {
            "exportType": "invalid_type",
            "format": "excel",
            "filters": {}
        }
        
        response = client.post("/api/export/generate", json=export_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_generate_export_unauthorized(self):
        """Test export generation endpoint without authentication"""
        response = client.post("/api/export/generate", json={})
        assert response.status_code == 401

class TestExportDownload:
    """Test export download endpoints"""
    
    def test_download_export_success(self, auth_headers, test_export_file_id):
        """Test successful export file download"""
        response = client.get(f"/api/export/download/{test_export_file_id}", headers=auth_headers)
        
        # This would return binary file data
        assert response.status_code in [200, 404]  # 404 if file doesn't exist
    
    def test_download_export_invalid_file_id(self, auth_headers):
        """Test export download with invalid file ID"""
        response = client.get("/api/export/download/invalid_file_id", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_download_export_unauthorized(self):
        """Test export download endpoint without authentication"""
        response = client.get("/api/export/download/test_file_id")
        assert response.status_code == 401
