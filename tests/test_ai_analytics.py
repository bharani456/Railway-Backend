"""
AI analysis and analytics tests - Task 19: Comprehensive Testing Suite
Tests for: POST /api/ai-analysis/analyze, GET /api/ai-analysis/reports, POST /api/ai-analysis/bulk-predict
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAIAnalysis:
    """Test AI analysis endpoints"""
    
    def test_analyze_data_success(self, auth_headers, test_qr_code_id):
        """Test successful AI data analysis"""
        analysis_data = {
            "qrCodeId": test_qr_code_id,
            "analysisType": "predictive",
            "inputData": {
                "inspectionHistory": [
                    {
                        "date": "2025-01-01",
                        "condition": "good",
                        "score": 95
                    }
                ],
                "maintenanceHistory": [
                    {
                        "date": "2024-12-01",
                        "type": "preventive",
                        "cost": 100.00
                    }
                ],
                "environmentalData": {
                    "temperature": 25.5,
                    "humidity": 60,
                    "trafficLoad": "high"
                }
            }
        }
        
        response = client.post("/api/ai-analysis/analyze", json=analysis_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "analysisReport" in data["data"]
    
    def test_analyze_data_invalid_qr_code(self, auth_headers):
        """Test AI analysis with invalid QR code"""
        analysis_data = {
            "qrCodeId": "invalid_qr_code_id",
            "analysisType": "predictive",
            "inputData": {}
        }
        
        response = client.post("/api/ai-analysis/analyze", json=analysis_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_ai_analysis_reports_success(self, auth_headers):
        """Test successful AI analysis reports listing"""
        response = client.get("/api/ai-analysis/reports", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "reports" in data["data"]
    
    def test_get_ai_analysis_reports_with_filters(self, auth_headers, test_qr_code_id):
        """Test AI analysis reports listing with filters"""
        response = client.get(
            f"/api/ai-analysis/reports?qrCodeId={test_qr_code_id}&analysisType=predictive&riskAssessment=high",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_bulk_predict_success(self, auth_headers, test_zone_id, test_fitting_type_id):
        """Test successful bulk AI prediction"""
        bulk_data = {
            "filters": {
                "zoneId": test_zone_id,
                "fittingTypeId": test_fitting_type_id,
                "installationDateRange": {
                    "start": "2024-01-01",
                    "end": "2024-12-31"
                }
            },
            "analysisType": "lifecycle"
        }
        
        response = client.post("/api/ai-analysis/bulk-predict", json=bulk_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "analysisResults" in data["data"]
        assert "summary" in data["data"]
    
    def test_ai_analysis_unauthorized(self):
        """Test AI analysis endpoints without authentication"""
        response = client.get("/api/ai-analysis/reports")
        assert response.status_code == 401
        
        response = client.post("/api/ai-analysis/analyze", json={})
        assert response.status_code == 401

class TestAnalytics:
    """Test analytics endpoints"""
    
    def test_get_performance_metrics_success(self, auth_headers):
        """Test successful performance metrics retrieval"""
        response = client.get("/api/analytics/performance-metrics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "metrics" in data["data"]
    
    def test_get_performance_metrics_with_filters(self, auth_headers):
        """Test performance metrics with filters"""
        response = client.get(
            "/api/analytics/performance-metrics?dateRange=2025-01-01,2025-12-31&groupBy=month&metrics=lifespan,failure_rate",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_quality_trends_success(self, auth_headers):
        """Test successful quality trends retrieval"""
        response = client.get("/api/analytics/quality-trends", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "qualityTrends" in data["data"]
    
    def test_get_quality_trends_with_filters(self, auth_headers, test_fitting_type_id, test_manufacturer_id):
        """Test quality trends with filters"""
        response = client.get(
            f"/api/analytics/quality-trends?dateRange=2025-01-01,2025-12-31&fittingType={test_fitting_type_id}&manufacturer={test_manufacturer_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_analytics_unauthorized(self):
        """Test analytics endpoints without authentication"""
        response = client.get("/api/analytics/performance-metrics")
        assert response.status_code == 401
        
        response = client.get("/api/analytics/quality-trends")
        assert response.status_code == 401
