"""
Inspection and maintenance models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.models.base import BaseDocument, Coordinates, PyObjectId

class InspectionChecklist(BaseModel):
    """Inspection checklist model"""
    
    item: str = Field(..., max_length=200)
    status: str = Field(..., pattern="^(pass|fail|na)$")
    remarks: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None

class InspectionBase(BaseModel):
    """Base inspection model"""
    
    qrCodeId: PyObjectId
    inspectorId: PyObjectId
    inspectionType: str = Field(..., max_length=50)
    inspectionDate: datetime = Field(default_factory=datetime.utcnow)
    inspectionLocation: Optional[str] = None
    inspectionCoordinates: Optional[Coordinates] = None
    visualCondition: str = Field(..., max_length=50)
    checklistData: List[InspectionChecklist] = []
    photos: List[str] = []
    recommendation: Optional[str] = None
    nextInspectionDue: Optional[datetime] = None
    status: str = Field(default="pending")
    remarks: Optional[str] = None
    weatherConditions: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None

class InspectionCreate(InspectionBase):
    """Inspection creation model"""
    
    pass

class InspectionUpdate(BaseModel):
    """Inspection update model"""
    
    visualCondition: Optional[str] = None
    checklistData: Optional[List[InspectionChecklist]] = None
    recommendation: Optional[str] = None
    nextInspectionDue: Optional[datetime] = None
    status: Optional[str] = None
    remarks: Optional[str] = None
    weatherConditions: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None

class InspectionResponse(InspectionBase):
    """Inspection response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    qrCode: Optional[Dict[str, Any]] = None
    inspector: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MaintenanceRecordBase(BaseModel):
    """Base maintenance record model"""
    
    qrCodeId: PyObjectId
    performedBy: PyObjectId
    maintenanceType: str = Field(..., max_length=50)
    maintenanceDate: datetime = Field(default_factory=datetime.utcnow)
    workDescription: str = Field(..., max_length=1000)
    partsReplaced: List[Dict[str, Any]] = []
    partsUsed: List[Dict[str, Any]] = []
    cost: Optional[float] = Field(None, ge=0)
    beforePhotos: List[str] = []
    afterPhotos: List[str] = []
    status: str = Field(default="completed")
    nextMaintenanceDue: Optional[datetime] = None
    qualityCheckPassed: Optional[bool] = None
    qualityCheckedBy: Optional[PyObjectId] = None
    qualityCheckDate: Optional[datetime] = None
    remarks: Optional[str] = None
    workOrderNumber: Optional[str] = Field(None, max_length=50)

class MaintenanceRecordCreate(MaintenanceRecordBase):
    """Maintenance record creation model"""
    
    pass

class MaintenanceRecordUpdate(BaseModel):
    """Maintenance record update model"""
    
    workDescription: Optional[str] = Field(None, max_length=1000)
    partsReplaced: Optional[List[Dict[str, Any]]] = None
    partsUsed: Optional[List[Dict[str, Any]]] = None
    cost: Optional[float] = Field(None, ge=0)
    status: Optional[str] = None
    nextMaintenanceDue: Optional[datetime] = None
    qualityCheckPassed: Optional[bool] = None
    qualityCheckedBy: Optional[PyObjectId] = None
    qualityCheckDate: Optional[datetime] = None
    remarks: Optional[str] = None
    workOrderNumber: Optional[str] = Field(None, max_length=50)

class MaintenanceRecordResponse(MaintenanceRecordBase):
    """Maintenance record response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    qrCode: Optional[Dict[str, Any]] = None
    performer: Optional[Dict[str, Any]] = None
    qualityChecker: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class InspectionListParams(BaseModel):
    """Inspection list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    qrCodeId: Optional[PyObjectId] = None
    inspectorId: Optional[PyObjectId] = None
    inspectionType: Optional[str] = None
    status: Optional[str] = None
    dateRange: Optional[str] = None
    sortBy: Optional[str] = Field("inspectionDate")
    sortOrder: str = Field("desc", pattern="^(asc|desc)$")

class MaintenanceRecordListParams(BaseModel):
    """Maintenance record list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    qrCodeId: Optional[PyObjectId] = None
    performedBy: Optional[PyObjectId] = None
    maintenanceType: Optional[str] = None
    status: Optional[str] = None
    dateRange: Optional[str] = None
    sortBy: Optional[str] = Field("maintenanceDate")
    sortOrder: str = Field("desc", pattern="^(asc|desc)$")

class InspectionStats(BaseModel):
    """Inspection statistics model"""
    
    totalInspections: int
    pendingInspections: int
    completedInspections: int
    inspectionsByType: Dict[str, int]
    inspectionsByStatus: Dict[str, int]
    inspectionsByInspector: Dict[str, int]
    averageInspectionTime: float

class MaintenanceRecordStats(BaseModel):
    """Maintenance record statistics model"""
    
    totalMaintenanceRecords: int
    completedMaintenance: int
    pendingMaintenance: int
    maintenanceByType: Dict[str, int]
    maintenanceByStatus: Dict[str, int]
    totalMaintenanceCost: float
    averageMaintenanceCost: float
