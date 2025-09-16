"""
Hierarchy management tests - Task 19: Comprehensive Testing Suite
Tests for: GET/POST /api/zones, GET/POST /api/divisions, GET/POST /api/stations
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestZoneManagement:
    """Test zone management endpoints"""
    
    def test_get_zones_success(self, auth_headers):
        """Test successful zone listing"""
        response = client.get("/api/zones", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "zones" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_zones_with_filters(self, auth_headers):
        """Test zone listing with filters"""
        response = client.get(
            "/api/zones?search=southern&status=active&page=1&limit=5",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_create_zone_success(self, auth_headers):
        """Test successful zone creation"""
        zone_data = {
            "name": "Test Zone",
            "code": "TZ",
            "description": "Test zone for testing",
            "headquarters": "Test City",
            "coordinates": {
                "lat": 13.0827,
                "lng": 80.2707
            }
        }
        
        response = client.post("/api/zones", json=zone_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "zone" in data["data"]
        assert data["data"]["zone"]["name"] == zone_data["name"]
    
    def test_create_zone_invalid_code(self, auth_headers):
        """Test zone creation with invalid code"""
        zone_data = {
            "name": "Test Zone",
            "code": "tz",  # Should be uppercase
            "description": "Test zone"
        }
        
        response = client.post("/api/zones", json=zone_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_zones_unauthorized(self):
        """Test zone endpoints without authentication"""
        response = client.get("/api/zones")
        assert response.status_code == 401
        
        response = client.post("/api/zones", json={})
        assert response.status_code == 401

class TestDivisionManagement:
    """Test division management endpoints"""
    
    def test_get_divisions_success(self, auth_headers):
        """Test successful division listing"""
        response = client.get("/api/divisions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "divisions" in data["data"]
    
    def test_create_division_success(self, auth_headers, test_zone_id):
        """Test successful division creation"""
        division_data = {
            "name": "Test Division",
            "code": "TD",
            "zoneId": test_zone_id,
            "description": "Test division for testing",
            "headquarters": "Test City"
        }
        
        response = client.post("/api/divisions", json=division_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "division" in data["data"]
    
    def test_create_division_invalid_zone(self, auth_headers):
        """Test division creation with invalid zone ID"""
        division_data = {
            "name": "Test Division",
            "code": "TD",
            "zoneId": "invalid_zone_id",
            "description": "Test division"
        }
        
        response = client.post("/api/divisions", json=division_data, headers=auth_headers)
        
        assert response.status_code == 400

class TestStationManagement:
    """Test station management endpoints"""
    
    def test_get_stations_success(self, auth_headers):
        """Test successful station listing"""
        response = client.get("/api/stations", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "stations" in data["data"]
    
    def test_create_station_success(self, auth_headers, test_division_id):
        """Test successful station creation"""
        station_data = {
            "name": "Test Station",
            "code": "TS",
            "divisionId": test_division_id,
            "description": "Test station for testing",
            "stationType": "Terminal",
            "coordinates": {
                "lat": 13.0827,
                "lng": 80.2707
            },
            "platformCount": 4
        }
        
        response = client.post("/api/stations", json=station_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "station" in data["data"]
    
    def test_get_stations_by_zone(self, auth_headers, test_zone_id):
        """Test station listing by zone"""
        response = client.get(f"/api/stations?zoneId={test_zone_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
