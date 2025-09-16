"""
Base Pydantic models and common schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class BaseDocument(BaseModel):
    """Base document model with common fields"""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    status: str = Field(default="active")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Coordinates(BaseModel):
    """GPS coordinates model"""
    
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    accuracy: Optional[float] = Field(None, ge=0, description="Accuracy in meters")
    altitude: Optional[float] = Field(None, description="Altitude in meters")

class Address(BaseModel):
    """Address model"""
    
    street: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: str = "India"
    coordinates: Optional[Coordinates] = None

class ContactInfo(BaseModel):
    """Contact information model"""
    
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    mobile: Optional[str] = Field(None, description="Mobile number")
    address: Optional[Address] = None

class PaginationParams(BaseModel):
    """Pagination parameters"""
    
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field("desc", regex="^(asc|desc)$", description="Sort order")

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    
    data: List[Any]
    pagination: Dict[str, Any]
    success: bool = True
    message: Optional[str] = None

class APIResponse(BaseModel):
    """Standard API response model"""
    
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    
    success: bool = False
    message: str
    error: str
    details: Optional[Dict[str, Any]] = None

# Enums
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    INSPECTOR = "inspector"
    OPERATOR = "operator"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class BatchStatus(str, Enum):
    MANUFACTURING = "manufacturing"
    MANUFACTURED = "manufactured"
    QUALITY_CHECK = "quality_check"
    APPROVED = "approved"
    REJECTED = "rejected"
    SHIPPED = "shipped"

class QRCodeStatus(str, Enum):
    GENERATED = "generated"
    PRINTED = "printed"
    VERIFIED = "verified"
    INSTALLED = "installed"
    IN_SERVICE = "in_service"
    MAINTENANCE_DUE = "maintenance_due"
    REPLACED = "replaced"
    RETIRED = "retired"

class InstallationStatus(str, Enum):
    INSTALLED = "installed"
    IN_SERVICE = "in_service"
    MAINTENANCE_DUE = "maintenance_due"
    REPLACED = "replaced"
    RETIRED = "retired"

class InspectionType(str, Enum):
    ROUTINE = "routine"
    SPECIAL = "special"
    EMERGENCY = "emergency"
    POST_MAINTENANCE = "post_maintenance"

class InspectionStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MaintenanceType(str, Enum):
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"
    ROUTINE = "routine"

class MaintenanceStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AnalysisType(str, Enum):
    PREDICTIVE = "predictive"
    DEFECT_DETECTION = "defect_detection"
    PERFORMANCE = "performance"
    LIFECYCLE = "lifecycle"
    RISK_ASSESSMENT = "risk_assessment"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationType(str, Enum):
    INSPECTION_DUE = "inspection_due"
    MAINTENANCE_DUE = "maintenance_due"
    QUALITY_ALERT = "quality_alert"
    SYSTEM_ALERT = "system_alert"
    ORDER_UPDATE = "order_update"
    BATCH_UPDATE = "batch_update"

class PortalName(str, Enum):
    UDM = "UDM"
    TMS = "TMS"

class RecordType(str, Enum):
    SUPPLY_ORDER = "supply_order"
    FITTING_BATCH = "fitting_batch"
    QR_CODE = "qr_code"
    INSTALLATION = "installation"
    INSPECTION = "inspection"
    MAINTENANCE = "maintenance"
