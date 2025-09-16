"""
User models and schemas
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.models.base import BaseDocument, UserRole, UserStatus, ContactInfo, PyObjectId

class UserBase(BaseModel):
    """Base user model"""
    
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    employeeId: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=15)
    role: UserRole
    zoneId: Optional[PyObjectId] = None
    divisionId: Optional[PyObjectId] = None
    stationId: Optional[PyObjectId] = None
    isActive: bool = True
    lastLoginAt: Optional[datetime] = None
    profilePicture: Optional[str] = None  # URL or file path
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('Phone number must contain only digits')
        return v

class UserCreate(UserBase):
    """User creation model"""
    
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    """User update model"""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    employeeId: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=15)
    role: Optional[UserRole] = None
    zoneId: Optional[PyObjectId] = None
    divisionId: Optional[PyObjectId] = None
    stationId: Optional[PyObjectId] = None
    isActive: Optional[bool] = None
    profilePicture: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('Phone number must contain only digits')
        return v

class UserResponse(UserBase):
    """User response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    status: str
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserLogin(BaseModel):
    """User login model"""
    
    email: EmailStr
    password: str
    deviceInfo: Optional[dict] = None

class UserSession(BaseModel):
    """User session model"""
    
    userId: PyObjectId
    token: str
    refreshToken: str
    deviceInfo: Optional[dict] = None
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None
    isActive: bool = True
    expiresAt: datetime
    lastActivity: Optional[datetime] = None

class UserSessionCreate(UserSession):
    """User session creation model"""
    
    pass

class UserSessionResponse(UserSession):
    """User session response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserProfile(BaseModel):
    """User profile model"""
    
    user: UserResponse
    permissions: List[str] = []
    accessibleZones: List[PyObjectId] = []
    accessibleDivisions: List[PyObjectId] = []
    accessibleStations: List[PyObjectId] = []

class UserListParams(BaseModel):
    """User list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    zoneId: Optional[PyObjectId] = None
    divisionId: Optional[PyObjectId] = None
    stationId: Optional[PyObjectId] = None
    sortBy: Optional[str] = Field("createdAt")
    sortOrder: str = Field("desc", regex="^(asc|desc)$")

class UserStats(BaseModel):
    """User statistics model"""
    
    totalUsers: int
    activeUsers: int
    inactiveUsers: int
    usersByRole: dict
    usersByZone: dict
    recentLogins: int
