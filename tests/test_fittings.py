"""
Fitting management tests - Task 19: Comprehensive Testing Suite
Tests for: GET/POST /api/fitting-categories, GET/POST /api/fitting-types
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestFittingCategoryManagement:
    """Test fitting category management endpoints"""
    
    def test_get_fitting_categories_success(self, auth_headers):
        """Test successful fitting category listing"""
        response = client.get("/api/fitting-categories", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "categories" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_fitting_categories_with_filters(self, auth_headers):
        """Test fitting category listing with filters"""
        response = client.get(
            "/api/fitting-categories?search=rail&status=active&isActive=true",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_create_fitting_category_success(self, auth_headers):
        """Test successful fitting category creation"""
        category_data = {
            "name": "Elastic Rail Clip",
            "code": "ERC",
            "description": "Elastic Rail Clip for track fastening",
            "specifications": {
                "material": "Spring Steel",
                "dimensions": {
                    "length": 150,
                    "width": 25,
                    "thickness": 8
                },
                "weight": 0.5,
                "tensileStrength": 1200
            },
            "warrantyPeriodMonths": 24,
            "standardCode": "IS:1234",
            "drawingNumber": "DRW-001"
        }
        
        response = client.post("/api/fitting-categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "category" in data["data"]
        assert data["data"]["category"]["name"] == category_data["name"]
    
    def test_create_fitting_category_invalid_code(self, auth_headers):
        """Test fitting category creation with invalid code"""
        category_data = {
            "name": "Test Category",
            "code": "tc",  # Should be uppercase
            "description": "Test category"
        }
        
        response = client.post("/api/fitting-categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_fitting_categories_unauthorized(self):
        """Test fitting category endpoints without authentication"""
        response = client.get("/api/fitting-categories")
        assert response.status_code == 401
        
        response = client.post("/api/fitting-categories", json={})
        assert response.status_code == 401

class TestFittingTypeManagement:
    """Test fitting type management endpoints"""
    
    def test_get_fitting_types_success(self, auth_headers):
        """Test successful fitting type listing"""
        response = client.get("/api/fitting-types", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "fittingTypes" in data["data"]
    
    def test_get_fitting_types_by_category(self, auth_headers, test_fitting_category_id):
        """Test fitting type listing by category"""
        response = client.get(
            f"/api/fitting-types?categoryId={test_fitting_category_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_create_fitting_type_success(self, auth_headers, test_fitting_category_id, test_manufacturer_id):
        """Test successful fitting type creation"""
        fitting_type_data = {
            "name": "Type A Rail Clip",
            "model": "A-100",
            "categoryId": test_fitting_category_id,
            "description": "Type A Elastic Rail Clip",
            "manufacturerId": test_manufacturer_id,
            "partNumber": "ERC-A100",
            "drawingNumber": "DRW-A100",
            "specifications": {
                "material": "Spring Steel",
                "dimensions": {
                    "length": 150,
                    "width": 25,
                    "thickness": 8
                }
            }
        }
        
        response = client.post("/api/fitting-types", json=fitting_type_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "fittingType" in data["data"]
        assert data["data"]["fittingType"]["name"] == fitting_type_data["name"]
    
    def test_create_fitting_type_invalid_model(self, auth_headers, test_fitting_category_id):
        """Test fitting type creation with invalid model"""
        fitting_type_data = {
            "name": "Test Type",
            "model": "invalid@model",  # Invalid characters
            "categoryId": test_fitting_category_id,
            "description": "Test type"
        }
        
        response = client.post("/api/fitting-types", json=fitting_type_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_fitting_types_unauthorized(self):
        """Test fitting type endpoints without authentication"""
        response = client.get("/api/fitting-types")
        assert response.status_code == 401
        
        response = client.post("/api/fitting-types", json={})
        assert response.status_code == 401
