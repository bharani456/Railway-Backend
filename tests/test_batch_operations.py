"""
Batch operations tests - Task 19: Comprehensive Testing Suite
Tests for: POST /api/batch-operations/import, POST /api/batch-operations/export
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestBatchImport:
    """Test batch import operations"""
    
    def test_batch_import_success(self, auth_headers):
        """Test successful batch import"""
        import_data = {
            "importType": "fittings",
            "data": [
                {
                    "name": "Test Fitting 1",
                    "code": "TF1",
                    "description": "Test fitting 1"
                },
                {
                    "name": "Test Fitting 2",
                    "code": "TF2",
                    "description": "Test fitting 2"
                }
            ],
            "options": {
                "skipDuplicates": True,
                "validateData": True
            }
        }
        
        response = client.post("/api/batch-operations/import", json=import_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "importId" in data["data"]
        assert "status" in data["data"]
        assert "totalRecords" in data["data"]
        assert "processedRecords" in data["data"]
    
    def test_batch_import_invalid_type(self, auth_headers):
        """Test batch import with invalid type"""
        import_data = {
            "importType": "invalid_type",
            "data": []
        }
        
        response = client.post("/api/batch-operations/import", json=import_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_batch_import_empty_data(self, auth_headers):
        """Test batch import with empty data"""
        import_data = {
            "importType": "fittings",
            "data": []
        }
        
        response = client.post("/api/batch-operations/import", json=import_data, headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_batch_import_unauthorized(self):
        """Test batch import endpoint without authentication"""
        response = client.post("/api/batch-operations/import", json={})
        assert response.status_code == 401

class TestBatchExport:
    """Test batch export operations"""
    
    def test_batch_export_success(self, auth_headers):
        """Test successful batch export"""
        export_data = {
            "exportType": "fittings",
            "filters": {
                "status": "active",
                "dateRange": {
                    "start": "2025-01-01",
                    "end": "2025-12-31"
                }
            },
            "format": "excel",
            "includeMedia": False
        }
        
        response = client.post("/api/batch-operations/export", json=export_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "exportId" in data["data"]
        assert "status" in data["data"]
        assert "estimatedRecords" in data["data"]
    
    def test_batch_export_invalid_type(self, auth_headers):
        """Test batch export with invalid type"""
        export_data = {
            "exportType": "invalid_type",
            "filters": {},
            "format": "excel"
        }
        
        response = client.post("/api/batch-operations/export", json=export_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_batch_export_invalid_format(self, auth_headers):
        """Test batch export with invalid format"""
        export_data = {
            "exportType": "fittings",
            "filters": {},
            "format": "invalid_format"
        }
        
        response = client.post("/api/batch-operations/export", json=export_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_batch_export_unauthorized(self):
        """Test batch export endpoint without authentication"""
        response = client.post("/api/batch-operations/export", json={})
        assert response.status_code == 401
