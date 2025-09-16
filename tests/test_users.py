"""
User management tests - Task 19: Comprehensive Testing Suite
Tests for: GET /api/users, POST /api/users, PUT /api/users/:id, DELETE /api/users/:id
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestUserManagement:
    """Test user management endpoints"""
    
    def test_get_users_success(self, auth_headers):
        """Test successful user listing"""
        response = client.get("/api/users", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "users" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_users_with_filters(self, auth_headers):
        """Test user listing with filters"""
        response = client.get(
            "/api/users?role=inspector&status=active&page=1&limit=5",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_users_unauthorized(self):
        """Test user listing without authentication"""
        response = client.get("/api/users")
        
        assert response.status_code == 401
    
    def test_create_user_success(self, auth_headers):
        """Test successful user creation"""
        user_data = {
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "TestPass123",
            "role": "inspector",
            "phone": "9876543210"
        }
        
        response = client.post("/api/users", json=user_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "user" in data["data"]
        assert data["data"]["user"]["email"] == user_data["email"]
    
    def test_create_user_invalid_email(self, auth_headers):
        """Test user creation with invalid email"""
        user_data = {
            "name": "Test User",
            "email": "invalid-email",
            "password": "TestPass123",
            "role": "inspector"
        }
        
        response = client.post("/api/users", json=user_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_create_user_weak_password(self, auth_headers):
        """Test user creation with weak password"""
        user_data = {
            "name": "Test User",
            "email": "testuser2@example.com",
            "password": "123",
            "role": "inspector"
        }
        
        response = client.post("/api/users", json=user_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_update_user_success(self, auth_headers, test_user_id):
        """Test successful user update"""
        update_data = {
            "name": "Updated Test User",
            "phone": "9876543211"
        }
        
        response = client.put(f"/api/users/{test_user_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["user"]["name"] == update_data["name"]
    
    def test_update_user_not_found(self, auth_headers):
        """Test user update with non-existent user"""
        update_data = {"name": "Updated Name"}
        
        response = client.put("/api/users/507f1f77bcf86cd799439011", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_delete_user_success(self, auth_headers, test_user_id):
        """Test successful user deletion (soft delete)"""
        response = client.delete(f"/api/users/{test_user_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted successfully" in data["message"]
    
    def test_delete_user_not_found(self, auth_headers):
        """Test user deletion with non-existent user"""
        response = client.delete("/api/users/507f1f77bcf86cd799439011", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_user_profile(self, auth_headers):
        """Test get user profile"""
        response = client.get("/api/users/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user" in data["data"]
    
    def test_update_user_profile(self, auth_headers):
        """Test update user profile"""
        profile_data = {
            "name": "Updated Profile Name",
            "phone": "9876543212"
        }
        
        response = client.put("/api/users/profile", json=profile_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
