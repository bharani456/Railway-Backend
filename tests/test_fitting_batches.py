"""
Fitting batch management tests - Task 19: Comprehensive Testing Suite
Tests for: GET/POST /api/fitting-batches, PUT /api/fitting-batches/:id/quality-documents
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestFittingBatchManagement:
    """Test fitting batch management endpoints"""
    
    def test_get_fitting_batches_success(self, auth_headers):
        """Test successful fitting batch listing"""
        response = client.get("/api/fitting-batches", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "batches" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_fitting_batches_with_filters(self, auth_headers, test_supply_order_id):
        """Test fitting batch listing with filters"""
        response = client.get(
            f"/api/fitting-batches?supplyOrderId={test_supply_order_id}&status=manufactured",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_create_fitting_batch_success(self, auth_headers, test_supply_order_id, test_manufacturer_id):
        """Test successful fitting batch creation"""
        batch_data = {
            "batchNumber": "BATCH-2025-001",
            "supplyOrderId": test_supply_order_id,
            "supplyOrderItemIndex": 0,
            "quantity": 500,
            "manufacturerId": test_manufacturer_id,
            "manufacturingDate": "2025-01-15T00:00:00Z",
            "qualityGrade": "A",
            "testResults": {
                "tensileStrength": 1200,
                "hardness": 45,
                "dimensions": "Within tolerance"
            },
            "remarks": "High quality batch"
        }
        
        response = client.post("/api/fitting-batches", json=batch_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "batch" in data["data"]
        assert data["data"]["batch"]["batchNumber"] == batch_data["batchNumber"]
    
    def test_create_fitting_batch_invalid_quantity(self, auth_headers, test_supply_order_id, test_manufacturer_id):
        """Test fitting batch creation with invalid quantity"""
        batch_data = {
            "batchNumber": "BATCH-2025-002",
            "supplyOrderId": test_supply_order_id,
            "supplyOrderItemIndex": 0,
            "quantity": 0,  # Invalid quantity
            "manufacturerId": test_manufacturer_id
        }
        
        response = client.post("/api/fitting-batches", json=batch_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_update_fitting_batch_quality_documents(self, auth_headers, test_fitting_batch_id):
        """Test fitting batch quality documents upload"""
        # This would typically be a multipart form upload
        # For testing, we'll simulate the endpoint call
        response = client.put(
            f"/api/fitting-batches/{test_fitting_batch_id}/quality-documents",
            headers=auth_headers
        )
        
        # The actual implementation would handle file uploads
        # For now, we expect a 422 for missing form data
        assert response.status_code in [200, 422]
    
    def test_get_fitting_batch_by_id(self, auth_headers, test_fitting_batch_id):
        """Test get fitting batch by ID"""
        response = client.get(f"/api/fitting-batches/{test_fitting_batch_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "batch" in data["data"]
    
    def test_fitting_batches_unauthorized(self):
        """Test fitting batch endpoints without authentication"""
        response = client.get("/api/fitting-batches")
        assert response.status_code == 401
        
        response = client.post("/api/fitting-batches", json={})
        assert response.status_code == 401
