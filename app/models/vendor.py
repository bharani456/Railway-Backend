"""
Vendor and manufacturer models
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.models.base import BaseDocument, ContactInfo, PyObjectId

class VendorBase(BaseModel):
    """Base vendor model"""
    
    name: str = Field(..., min_length=2, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    gstNumber: Optional[str] = Field(None, max_length=15)
    panNumber: Optional[str] = Field(None, max_length=10)
    contactInfo: ContactInfo
    address: Optional[str] = Field(None, max_length=500)
    city: str = Field(..., max_length=50)
    state: str = Field(..., max_length=50)
    pincode: str = Field(..., max_length=10)
    country: str = Field(default="India", max_length=50)
    website: Optional[str] = Field(None, max_length=200)
    registrationDate: Optional[datetime] = None
    licenseNumber: Optional[str] = Field(None, max_length=50)
    licenseExpiry: Optional[datetime] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    isVerified: bool = False
    
    @validator('gstNumber')
    def validate_gst(cls, v):
        if v and len(v) != 15:
            raise ValueError('GST number must be 15 characters long')
        return v
    
    @validator('panNumber')
    def validate_pan(cls, v):
        if v and len(v) != 10:
            raise ValueError('PAN number must be 10 characters long')
        return v

class VendorCreate(VendorBase):
    """Vendor creation model"""
    
    pass

class VendorUpdate(BaseModel):
    """Vendor update model"""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    gstNumber: Optional[str] = Field(None, max_length=15)
    panNumber: Optional[str] = Field(None, max_length=10)
    contactInfo: Optional[ContactInfo] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    pincode: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=200)
    licenseNumber: Optional[str] = Field(None, max_length=50)
    licenseExpiry: Optional[datetime] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    isVerified: Optional[bool] = None

class VendorResponse(VendorBase):
    """Vendor response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    status: str
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ManufacturerBase(BaseModel):
    """Base manufacturer model"""
    
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    contactInfo: ContactInfo
    address: Optional[str] = Field(None, max_length=500)
    city: str = Field(..., max_length=50)
    state: str = Field(..., max_length=50)
    pincode: str = Field(..., max_length=10)
    country: str = Field(default="India", max_length=50)
    website: Optional[str] = Field(None, max_length=200)
    licenseNumber: str = Field(..., max_length=50)
    licenseExpiry: Optional[datetime] = None
    certificationNumber: Optional[str] = Field(None, max_length=50)
    certificationExpiry: Optional[datetime] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    isVerified: bool = False
    specializations: Optional[List[str]] = []
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isupper():
            raise ValueError('Manufacturer code must be uppercase')
        return v

class ManufacturerCreate(ManufacturerBase):
    """Manufacturer creation model"""
    
    pass

class ManufacturerUpdate(BaseModel):
    """Manufacturer update model"""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    contactInfo: Optional[ContactInfo] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    pincode: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=200)
    licenseNumber: Optional[str] = Field(None, max_length=50)
    licenseExpiry: Optional[datetime] = None
    certificationNumber: Optional[str] = Field(None, max_length=50)
    certificationExpiry: Optional[datetime] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    isVerified: Optional[bool] = None
    specializations: Optional[List[str]] = None
    
    @validator('code')
    def validate_code(cls, v):
        if v and not v.isupper():
            raise ValueError('Manufacturer code must be uppercase')
        return v

class ManufacturerResponse(ManufacturerBase):
    """Manufacturer response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    status: str
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class VendorListParams(BaseModel):
    """Vendor list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    status: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    isVerified: Optional[bool] = None
    sortBy: Optional[str] = Field("name")
    sortOrder: str = Field("asc", pattern="^(asc|desc)$")

class ManufacturerListParams(BaseModel):
    """Manufacturer list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    status: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    isVerified: Optional[bool] = None
    sortBy: Optional[str] = Field("name")
    sortOrder: str = Field("asc", pattern="^(asc|desc)$")

class VendorStats(BaseModel):
    """Vendor statistics model"""
    
    totalVendors: int
    verifiedVendors: int
    unverifiedVendors: int
    vendorsByState: dict
    averageRating: float
    topRatedVendors: List[VendorResponse]

class ManufacturerStats(BaseModel):
    """Manufacturer statistics model"""
    
    totalManufacturers: int
    verifiedManufacturers: int
    unverifiedManufacturers: int
    manufacturersByState: dict
    averageRating: float
    topRatedManufacturers: List[ManufacturerResponse]
