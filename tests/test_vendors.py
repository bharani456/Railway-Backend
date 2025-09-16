"""
Vendor and manufacturer management tests - Task 19: Comprehensive Testing Suite
Tests for: GET/POST /api/vendors, GET/POST /api/manufacturers
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestVendorManagement:
    """Test vendor management endpoints"""
    
    def test_get_vendors_success(self, auth_headers):
        """Test successful vendor listing"""
        response = client.get("/api/vendors", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "vendors" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_vendors_with_filters(self, auth_headers):
        """Test vendor listing with filters"""
        response = client.get(
            "/api/vendors?search=abc&status=active&city=chennai&isVerified=true",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_create_vendor_success(self, auth_headers):
        """Test successful vendor creation"""
        vendor_data = {
            "name": "ABC Railways Supplies",
            "code": "ARS",
            "gstNumber": "29ABCDE1234F1Z5",
            "panNumber": "ABCDE1234F",
            "contactInfo": {
                "email": "contact@abc.com",
                "phone": "9876543210"
            },
            "address": "123 Railway Street",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "pincode": "600001",
            "website": "https://abc.com",
            "licenseNumber": "LIC123456"
        }
        
        response = client.post("/api/vendors", json=vendor_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "vendor" in data["data"]
        assert data["data"]["vendor"]["name"] == vendor_data["name"]
    
    def test_create_vendor_invalid_gst(self, auth_headers):
        """Test vendor creation with invalid GST number"""
        vendor_data = {
            "name": "Test Vendor",
            "gstNumber": "invalid_gst",
            "contactInfo": {
                "email": "test@example.com",
                "phone": "9876543210"
            },
            "city": "Chennai",
            "state": "Tamil Nadu",
            "pincode": "600001"
        }
        
        response = client.post("/api/vendors", json=vendor_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_create_vendor_invalid_pan(self, auth_headers):
        """Test vendor creation with invalid PAN number"""
        vendor_data = {
            "name": "Test Vendor",
            "panNumber": "invalid_pan",
            "contactInfo": {
                "email": "test@example.com",
                "phone": "9876543210"
            },
            "city": "Chennai",
            "state": "Tamil Nadu",
            "pincode": "600001"
        }
        
        response = client.post("/api/vendors", json=vendor_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_vendors_unauthorized(self):
        """Test vendor endpoints without authentication"""
        response = client.get("/api/vendors")
        assert response.status_code == 401
        
        response = client.post("/api/vendors", json={})
        assert response.status_code == 401

class TestManufacturerManagement:
    """Test manufacturer management endpoints"""
    
    def test_get_manufacturers_success(self, auth_headers):
        """Test successful manufacturer listing"""
        response = client.get("/api/manufacturers", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "manufacturers" in data["data"]
    
    def test_create_manufacturer_success(self, auth_headers):
        """Test successful manufacturer creation"""
        manufacturer_data = {
            "name": "Steel Works Ltd",
            "code": "SWL",
            "contactInfo": {
                "email": "info@steelworks.com",
                "phone": "9876543211"
            },
            "address": "456 Industrial Area",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "licenseNumber": "MFG123456",
            "certificationNumber": "CERT789012",
            "specializations": ["Steel", "Rail Components"]
        }
        
        response = client.post("/api/manufacturers", json=manufacturer_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "manufacturer" in data["data"]
        assert data["data"]["manufacturer"]["name"] == manufacturer_data["name"]
    
    def test_create_manufacturer_invalid_code(self, auth_headers):
        """Test manufacturer creation with invalid code"""
        manufacturer_data = {
            "name": "Test Manufacturer",
            "code": "tm",  # Should be uppercase
            "contactInfo": {
                "email": "test@example.com",
                "phone": "9876543211"
            },
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "licenseNumber": "LIC123456"
        }
        
        response = client.post("/api/manufacturers", json=manufacturer_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_manufacturers_unauthorized(self):
        """Test manufacturer endpoints without authentication"""
        response = client.get("/api/manufacturers")
        assert response.status_code == 401
        
        response = client.post("/api/manufacturers", json={})
        assert response.status_code == 401
