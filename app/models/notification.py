"""
Notification and search models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

from app.models.base import BaseDocument, PyObjectId

class NotificationType(str, Enum):
    """Notification type enumeration"""
    
    INSPECTION_DUE = "inspection_due"
    MAINTENANCE_DUE = "maintenance_due"
    QUALITY_ALERT = "quality_alert"
    SYSTEM_ALERT = "system_alert"
    BATCH_READY = "batch_ready"
    ORDER_STATUS = "order_status"
    INTEGRATION_ERROR = "integration_error"
    USER_ACTION = "user_action"

class NotificationBase(BaseModel):
    """Base notification model"""
    
    userId: PyObjectId
    type: NotificationType
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=1000)
    data: Optional[Dict[str, Any]] = {}
    isRead: bool = False
    priority: str = Field(default="normal")
    expiresAt: Optional[datetime] = None
    actionUrl: Optional[str] = None
    actionText: Optional[str] = None

class NotificationCreate(NotificationBase):
    """Notification creation model"""
    
    pass

class NotificationUpdate(BaseModel):
    """Notification update model"""
    
    isRead: Optional[bool] = None
    priority: Optional[str] = None
    expiresAt: Optional[datetime] = None
    actionUrl: Optional[str] = None
    actionText: Optional[str] = None

class NotificationResponse(NotificationBase):
    """Notification response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    user: Optional[Dict[str, Any]] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SearchResult(BaseModel):
    """Search result model"""
    
    type: str
    id: PyObjectId
    title: str
    description: Optional[str] = None
    relevanceScore: float = Field(..., ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = {}
    url: Optional[str] = None

class SearchResponse(BaseModel):
    """Search response model"""
    
    results: List[SearchResult]
    pagination: Dict[str, Any]
    facets: Optional[Dict[str, List[Dict[str, Any]]]] = {}
    totalResults: int
    searchTime: float

class FittingSearchParams(BaseModel):
    """Fitting search parameters"""
    
    query: str = Field(..., min_length=1)
    filters: Optional[Dict[str, Any]] = {}
    sort: str = Field(default="relevance")
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    zoneId: Optional[PyObjectId] = None
    divisionId: Optional[PyObjectId] = None
    stationId: Optional[PyObjectId] = None
    fittingType: Optional[str] = None
    status: Optional[str] = None
    dateRange: Optional[str] = None

class LocationSearchParams(BaseModel):
    """Location search parameters"""
    
    query: str = Field(..., min_length=1)
    type: Optional[str] = None
    zoneId: Optional[PyObjectId] = None
    divisionId: Optional[PyObjectId] = None
    limit: int = Field(10, ge=1, le=100)

class NotificationListParams(BaseModel):
    """Notification list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    userId: Optional[PyObjectId] = None
    type: Optional[NotificationType] = None
    isRead: Optional[bool] = None
    priority: Optional[str] = None
    dateRange: Optional[str] = None
    sortBy: Optional[str] = Field("createdAt")
    sortOrder: str = Field("desc", regex="^(asc|desc)$")

class NotificationStats(BaseModel):
    """Notification statistics model"""
    
    totalNotifications: int
    unreadNotifications: int
    notificationsByType: Dict[str, int]
    notificationsByPriority: Dict[str, int]
    averageResponseTime: float
    readRate: float

class SearchStats(BaseModel):
    """Search statistics model"""
    
    totalSearches: int
    searchesByType: Dict[str, int]
    averageSearchTime: float
    topQueries: List[Dict[str, Any]]
    searchSuccessRate: float
