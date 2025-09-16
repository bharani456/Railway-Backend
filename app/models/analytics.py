"""
Analytics and AI analysis models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

from app.models.base import BaseDocument, PyObjectId

class AnalysisType(str, Enum):
    """Analysis type enumeration"""
    
    PREDICTIVE = "predictive"
    DEFECT_DETECTION = "defect_detection"
    LIFECYCLE = "lifecycle"
    PERFORMANCE = "performance"
    RISK_ASSESSMENT = "risk_assessment"

class RiskLevel(str, Enum):
    """Risk level enumeration"""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AIAnalysisReportBase(BaseModel):
    """Base AI analysis report model"""
    
    qrCodeId: PyObjectId
    analysisType: AnalysisType
    inputData: Dict[str, Any] = {}
    analysisResults: Dict[str, Any] = {}
    riskLevel: RiskLevel
    confidenceScore: float = Field(..., ge=0, le=1)
    recommendations: List[str] = []
    predictedFailureDate: Optional[datetime] = None
    maintenanceRecommendation: Optional[str] = None
    status: str = Field(default="completed")
    processedAt: datetime = Field(default_factory=datetime.utcnow)
    processingTime: Optional[float] = None
    modelVersion: Optional[str] = None
    remarks: Optional[str] = None

class AIAnalysisReportCreate(AIAnalysisReportBase):
    """AI analysis report creation model"""
    
    pass

class AIAnalysisReportUpdate(BaseModel):
    """AI analysis report update model"""
    
    analysisResults: Optional[Dict[str, Any]] = None
    riskLevel: Optional[RiskLevel] = None
    confidenceScore: Optional[float] = Field(None, ge=0, le=1)
    recommendations: Optional[List[str]] = None
    predictedFailureDate: Optional[datetime] = None
    maintenanceRecommendation: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

class AIAnalysisReportResponse(AIAnalysisReportBase):
    """AI analysis report response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    qrCode: Optional[Dict[str, Any]] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    
    averageLifespan: float
    failureRate: float
    maintenanceCost: float
    inspectionCompliance: float
    qualityScore: float
    efficiency: float
    uptime: float

class QualityTrends(BaseModel):
    """Quality trends model"""
    
    period: str
    qualityScore: float
    defectRate: float
    maintenanceFrequency: float
    costPerUnit: float

class DashboardReport(BaseModel):
    """Dashboard report model"""
    
    totalFittings: int
    activeInstallations: int
    pendingInspections: int
    maintenanceDue: int
    riskDistribution: Dict[str, int]
    performanceMetrics: PerformanceMetrics
    qualityTrends: List[QualityTrends]
    alerts: List[Dict[str, Any]]

class InventoryReport(BaseModel):
    """Inventory report model"""
    
    inventoryByType: List[Dict[str, Any]]
    locationWiseStock: List[Dict[str, Any]]
    lowStockAlerts: List[Dict[str, Any]]
    totalValue: float
    averageStockLevel: float

class AnalyticsParams(BaseModel):
    """Analytics parameters model"""
    
    dateRange: Optional[str] = None
    groupBy: str = Field(default="month")
    metrics: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    zoneId: Optional[PyObjectId] = None
    divisionId: Optional[PyObjectId] = None
    stationId: Optional[PyObjectId] = None
    fittingTypeId: Optional[PyObjectId] = None
    manufacturerId: Optional[PyObjectId] = None

class AIAnalysisListParams(BaseModel):
    """AI analysis list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    qrCodeId: Optional[PyObjectId] = None
    analysisType: Optional[AnalysisType] = None
    riskLevel: Optional[RiskLevel] = None
    status: Optional[str] = None
    dateRange: Optional[str] = None
    sortBy: Optional[str] = Field("processedAt")
    sortOrder: str = Field("desc", regex="^(asc|desc)$")

class BulkAnalysisRequest(BaseModel):
    """Bulk analysis request model"""
    
    filters: Dict[str, Any] = {}
    analysisType: AnalysisType
    batchSize: int = Field(default=100, ge=1, le=1000)
    priority: str = Field(default="normal")

class BulkAnalysisResponse(BaseModel):
    """Bulk analysis response model"""
    
    analysisResults: List[Dict[str, Any]]
    summary: Dict[str, Any]
    batchId: str
    status: str
    totalAnalyzed: int
    highRiskCount: int
    mediumRiskCount: int
    lowRiskCount: int
    criticalRiskCount: int

class AIAnalysisStats(BaseModel):
    """AI analysis statistics model"""
    
    totalAnalyses: int
    analysesByType: Dict[str, int]
    analysesByRiskLevel: Dict[str, int]
    averageConfidenceScore: float
    averageProcessingTime: float
    successRate: float
    failureRate: float
