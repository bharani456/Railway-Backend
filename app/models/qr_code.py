"""
QR code and installation models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.models.base import BaseDocument, Coordinates, PyObjectId

class QRCodeBase(BaseModel):
    """Base QR code model"""
    
    qrCode: str = Field(..., min_length=10, max_length=100)
    fittingBatchId: PyObjectId
    sequenceNumber: int = Field(..., ge=1)
    status: str = Field(default="generated")
    generatedAt: datetime = Field(default_factory=datetime.utcnow)
    markingMachineId: Optional[str] = None
    markingOperatorId: Optional[PyObjectId] = None
    printQualityScore: Optional[float] = Field(None, ge=0, le=1)
    verificationStatus: Optional[str] = None
    verifiedAt: Optional[datetime] = None
    verifiedBy: Optional[PyObjectId] = None
    remarks: Optional[str] = None
    
    @validator('qrCode')
    def validate_qr_code(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('QR code must contain only alphanumeric characters, hyphens, and underscores')
        return v

class QRCodeCreate(QRCodeBase):
    """QR code creation model"""
    
    pass

class QRCodeUpdate(BaseModel):
    """QR code update model"""
    
    status: Optional[str] = None
    printQualityScore: Optional[float] = Field(None, ge=0, le=1)
    verificationStatus: Optional[str] = None
    verifiedAt: Optional[datetime] = None
    verifiedBy: Optional[PyObjectId] = None
    remarks: Optional[str] = None

class QRCodeResponse(QRCodeBase):
    """QR code response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    batch: Optional[Dict[str, Any]] = None
    fittingType: Optional[Dict[str, Any]] = None
    installation: Optional[Dict[str, Any]] = None
    lastInspection: Optional[Dict[str, Any]] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class QRCodeScanLog(BaseModel):
    """QR code scan log model"""
    
    qrCodeId: PyObjectId
    scannedBy: PyObjectId
    scanPurpose: str = Field(..., max_length=50)
    scanLocation: Optional[str] = None
    scanCoordinates: Optional[Coordinates] = None
    deviceInfo: Optional[Dict[str, Any]] = None
    scanDate: datetime = Field(default_factory=datetime.utcnow)
    remarks: Optional[str] = None

class InstallationBase(BaseModel):
    """Base installation model"""
    
    qrCodeId: PyObjectId
    zoneId: PyObjectId
    divisionId: Optional[PyObjectId] = None
    stationId: Optional[PyObjectId] = None
    trackSection: str = Field(..., max_length=100)
    kilometerPost: Optional[str] = Field(None, max_length=20)
    installationCoordinates: Coordinates
    installationDate: datetime = Field(default_factory=datetime.utcnow)
    installedBy: PyObjectId
    status: str = Field(default="installed")
    warrantyStartDate: Optional[datetime] = None
    warrantyEndDate: Optional[datetime] = None
    installationType: Optional[str] = None
    remarks: Optional[str] = None

class InstallationCreate(InstallationBase):
    """Installation creation model"""
    
    pass

class InstallationUpdate(BaseModel):
    """Installation update model"""
    
    status: Optional[str] = None
    warrantyStartDate: Optional[datetime] = None
    warrantyEndDate: Optional[datetime] = None
    installationType: Optional[str] = None
    remarks: Optional[str] = None

class InstallationResponse(InstallationBase):
    """Installation response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    qrCode: Optional[Dict[str, Any]] = None
    zone: Optional[Dict[str, Any]] = None
    division: Optional[Dict[str, Any]] = None
    station: Optional[Dict[str, Any]] = None
    installer: Optional[Dict[str, Any]] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class QRCodeListParams(BaseModel):
    """QR code list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    status: Optional[str] = None
    fittingBatchId: Optional[PyObjectId] = None
    dateRange: Optional[str] = None
    sortBy: Optional[str] = Field("generatedAt")
    sortOrder: str = Field("desc", regex="^(asc|desc)$")

class InstallationListParams(BaseModel):
    """Installation list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    status: Optional[str] = None
    zoneId: Optional[PyObjectId] = None
    divisionId: Optional[PyObjectId] = None
    stationId: Optional[PyObjectId] = None
    trackSection: Optional[str] = None
    dateRange: Optional[str] = None
    sortBy: Optional[str] = Field("installationDate")
    sortOrder: str = Field("desc", regex="^(asc|desc)$")

class QRCodeStats(BaseModel):
    """QR code statistics model"""
    
    totalQRCodes: int
    generatedQRCodes: int
    verifiedQRCodes: int
    installedQRCodes: int
    qrCodesByStatus: Dict[str, int]
    qrCodesByBatch: Dict[str, int]
    averagePrintQuality: float

class InstallationStats(BaseModel):
    """Installation statistics model"""
    
    totalInstallations: int
    activeInstallations: int
    maintenanceDue: int
    installationsByStatus: Dict[str, int]
    installationsByZone: Dict[str, int]
    installationsByTrackSection: Dict[str, int]
