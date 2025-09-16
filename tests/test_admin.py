"""
Administration and configuration tests - Task 19: Comprehensive Testing Suite
Tests for: GET /api/admin/system-status, GET /api/admin/audit-logs, POST /api/admin/backup
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSystemStatus:
    """Test system status endpoints"""
    
    def test_get_system_status_success(self, auth_headers):
        """Test successful system status retrieval"""
        response = client.get("/api/admin/system-status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "database" in data["data"]
        assert "redis" in data["data"]
        assert "storage" in data["data"]
        assert "api" in data["data"]
    
    def test_system_status_unauthorized(self):
        """Test system status endpoint without authentication"""
        response = client.get("/api/admin/system-status")
        assert response.status_code == 401

class TestAuditLogs:
    """Test audit logs endpoints"""
    
    def test_get_audit_logs_success(self, auth_headers):
        """Test successful audit logs retrieval"""
        response = client.get("/api/admin/audit-logs", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "auditLogs" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_audit_logs_with_filters(self, auth_headers, test_user_id):
        """Test audit logs retrieval with filters"""
        response = client.get(
            f"/api/admin/audit-logs?userId={test_user_id}&action=create&resource=user&dateRange=2025-01-01,2025-12-31",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_audit_logs_unauthorized(self):
        """Test audit logs endpoint without authentication"""
        response = client.get("/api/admin/audit-logs")
        assert response.status_code == 401

class TestBackupManagement:
    """Test backup management endpoints"""
    
    def test_create_backup_success(self, auth_headers):
        """Test successful backup creation"""
        backup_data = {
            "backupType": "full",
            "includeMedia": True,
            "description": "Scheduled backup"
        }
        
        response = client.post("/api/admin/backup", json=backup_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "backupId" in data["data"]
        assert "status" in data["data"]
    
    def test_create_backup_invalid_type(self, auth_headers):
        """Test backup creation with invalid type"""
        backup_data = {
            "backupType": "invalid_type",
            "includeMedia": True
        }
        
        response = client.post("/api/admin/backup", json=backup_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_backup_unauthorized(self):
        """Test backup endpoint without authentication"""
        response = client.post("/api/admin/backup", json={})
        assert response.status_code == 401

class TestConfiguration:
    """Test configuration endpoints"""
    
    def test_get_configuration_success(self, auth_headers):
        """Test successful configuration retrieval"""
        response = client.get("/api/admin/configuration", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "configuration" in data["data"]
    
    def test_update_configuration_success(self, auth_headers):
        """Test successful configuration update"""
        config_data = {
            "maxUploadSize": 10485760,
            "sessionTimeout": 3600,
            "enableNotifications": True
        }
        
        response = client.put("/api/admin/configuration", json=config_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "configuration" in data["data"]
    
    def test_configuration_unauthorized(self):
        """Test configuration endpoints without authentication"""
        response = client.get("/api/admin/configuration")
        assert response.status_code == 401
        
        response = client.put("/api/admin/configuration", json={})
        assert response.status_code == 401
