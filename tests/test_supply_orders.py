"""
Supply order management tests - Task 19: Comprehensive Testing Suite
Tests for: GET/POST /api/supply-orders, PUT /api/supply-orders/:id/status
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSupplyOrderManagement:
    """Test supply order management endpoints"""
    
    def test_get_supply_orders_success(self, auth_headers):
        """Test successful supply order listing"""
        response = client.get("/api/supply-orders", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "orders" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_supply_orders_with_filters(self, auth_headers, test_vendor_id):
        """Test supply order listing with filters"""
        response = client.get(
            f"/api/supply-orders?status=pending&vendorId={test_vendor_id}&dateRange=2025-01-01,2025-12-31",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_create_supply_order_success(self, auth_headers, test_vendor_id, test_fitting_type_id):
        """Test successful supply order creation"""
        supply_order_data = {
            "orderNumber": "SO-2025-001",
            "vendorId": test_vendor_id,
            "orderDate": "2025-01-01T00:00:00Z",
            "expectedDeliveryDate": "2025-02-01T00:00:00Z",
            "items": [
                {
                    "fittingTypeId": test_fitting_type_id,
                    "quantity": 1000,
                    "unitPrice": 50.00,
                    "totalPrice": 50000.00,
                    "deliveryDate": "2025-02-01T00:00:00Z"
                }
            ],
            "totalAmount": 50000.00,
            "currency": "INR",
            "priority": "normal",
            "purchaseOrderNumber": "PO-2025-001"
        }
        
        response = client.post("/api/supply-orders", json=supply_order_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "order" in data["data"]
        assert data["data"]["order"]["orderNumber"] == supply_order_data["orderNumber"]
    
    def test_create_supply_order_invalid_amount(self, auth_headers, test_vendor_id, test_fitting_type_id):
        """Test supply order creation with invalid amount"""
        supply_order_data = {
            "orderNumber": "SO-2025-002",
            "vendorId": test_vendor_id,
            "items": [
                {
                    "fittingTypeId": test_fitting_type_id,
                    "quantity": 1000,
                    "unitPrice": 50.00,
                    "totalPrice": 50000.00
                }
            ],
            "totalAmount": -1000.00  # Invalid negative amount
        }
        
        response = client.post("/api/supply-orders", json=supply_order_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_update_supply_order_status_success(self, auth_headers, test_supply_order_id):
        """Test successful supply order status update"""
        status_data = {
            "status": "delivered",
            "actualDeliveryDate": "2025-02-01T00:00:00Z",
            "remarks": "Delivered on time"
        }
        
        response = client.put(
            f"/api/supply-orders/{test_supply_order_id}/status",
            json=status_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["order"]["status"] == status_data["status"]
    
    def test_update_supply_order_status_invalid_id(self, auth_headers):
        """Test supply order status update with invalid ID"""
        status_data = {
            "status": "delivered",
            "actualDeliveryDate": "2025-02-01T00:00:00Z"
        }
        
        response = client.put(
            "/api/supply-orders/invalid_id/status",
            json=status_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_get_supply_order_by_id(self, auth_headers, test_supply_order_id):
        """Test get supply order by ID"""
        response = client.get(f"/api/supply-orders/{test_supply_order_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "order" in data["data"]
    
    def test_supply_orders_unauthorized(self):
        """Test supply order endpoints without authentication"""
        response = client.get("/api/supply-orders")
        assert response.status_code == 401
        
        response = client.post("/api/supply-orders", json={})
        assert response.status_code == 401
