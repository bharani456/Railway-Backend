"""
Reports tests - Task 19: Comprehensive Testing Suite
Tests for: GET /api/reports/dashboard, GET /api/reports/performance, GET /api/reports/inventory
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestReports:
    """Test reports endpoints"""
    
    def test_get_dashboard_report_success(self, auth_headers):
        """Test successful dashboard report retrieval"""
        response = client.get("/api/reports/dashboard", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "totalFittings" in data["data"]
        assert "activeInstallations" in data["data"]
        assert "pendingInspections" in data["data"]
        assert "maintenanceDue" in data["data"]
        assert "riskDistribution" in data["data"]
    
    def test_get_dashboard_report_with_filters(self, auth_headers, test_zone_id, test_division_id):
        """Test dashboard report with filters"""
        response = client.get(
            f"/api/reports/dashboard?zoneId={test_zone_id}&divisionId={test_division_id}&dateRange=2025-01-01,2025-12-31",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_performance_report_success(self, auth_headers):
        """Test successful performance report retrieval"""
        response = client.get("/api/reports/performance", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "reportData" in data["data"]
    
    def test_get_performance_report_with_filters(self, auth_headers):
        """Test performance report with filters"""
        response = client.get(
            "/api/reports/performance?reportType=efficiency&format=json",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_inventory_report_success(self, auth_headers):
        """Test successful inventory report retrieval"""
        response = client.get("/api/reports/inventory", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "inventoryByType" in data["data"]
        assert "locationWiseStock" in data["data"]
        assert "lowStockAlerts" in data["data"]
    
    def test_get_inventory_report_with_filters(self, auth_headers):
        """Test inventory report with filters"""
        response = client.get(
            "/api/reports/inventory?status=active&fittingTypes=type1,type2",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_reports_unauthorized(self):
        """Test reports endpoints without authentication"""
        response = client.get("/api/reports/dashboard")
        assert response.status_code == 401
        
        response = client.get("/api/reports/performance")
        assert response.status_code == 401
        
        response = client.get("/api/reports/inventory")
        assert response.status_code == 401
