"""
Fitting category and type models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.models.base import BaseDocument, PyObjectId

class TechnicalSpecification(BaseModel):
    """Technical specification model"""
    
    material: Optional[str] = None
    dimensions: Optional[Dict[str, float]] = None
    weight: Optional[float] = None
    tensileStrength: Optional[float] = None
    hardness: Optional[float] = None
    temperatureRange: Optional[Dict[str, float]] = None
    corrosionResistance: Optional[str] = None
    otherSpecs: Optional[Dict[str, Any]] = None

class FittingCategoryBase(BaseModel):
    """Base fitting category model"""
    
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    description: Optional[str] = Field(None, max_length=500)
    specifications: Optional[TechnicalSpecification] = None
    warrantyPeriodMonths: Optional[int] = Field(None, ge=0)
    standardCode: Optional[str] = Field(None, max_length=50)
    drawingNumber: Optional[str] = Field(None, max_length=50)
    imageUrl: Optional[str] = None
    isActive: bool = True
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isupper():
            raise ValueError('Category code must be uppercase')
        return v

class FittingCategoryCreate(FittingCategoryBase):
    """Fitting category creation model"""
    
    pass

class FittingCategoryUpdate(BaseModel):
    """Fitting category update model"""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    description: Optional[str] = Field(None, max_length=500)
    specifications: Optional[TechnicalSpecification] = None
    warrantyPeriodMonths: Optional[int] = Field(None, ge=0)
    standardCode: Optional[str] = Field(None, max_length=50)
    drawingNumber: Optional[str] = Field(None, max_length=50)
    imageUrl: Optional[str] = None
    isActive: Optional[bool] = None
    
    @validator('code')
    def validate_code(cls, v):
        if v and not v.isupper():
            raise ValueError('Category code must be uppercase')
        return v

class FittingCategoryResponse(FittingCategoryBase):
    """Fitting category response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    status: str
    fittingTypeCount: Optional[int] = 0
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class FittingTypeBase(BaseModel):
    """Base fitting type model"""
    
    name: str = Field(..., min_length=2, max_length=100)
    model: str = Field(..., min_length=2, max_length=50)
    categoryId: PyObjectId
    description: Optional[str] = Field(None, max_length=500)
    specifications: Optional[TechnicalSpecification] = None
    manufacturerId: Optional[PyObjectId] = None
    partNumber: Optional[str] = Field(None, max_length=50)
    drawingNumber: Optional[str] = Field(None, max_length=50)
    imageUrl: Optional[str] = None
    isActive: bool = True
    
    @validator('model')
    def validate_model(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Model must contain only alphanumeric characters, hyphens, and underscores')
        return v

class FittingTypeCreate(FittingTypeBase):
    """Fitting type creation model"""
    
    pass

class FittingTypeUpdate(BaseModel):
    """Fitting type update model"""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    model: Optional[str] = Field(None, min_length=2, max_length=50)
    categoryId: Optional[PyObjectId] = None
    description: Optional[str] = Field(None, max_length=500)
    specifications: Optional[TechnicalSpecification] = None
    manufacturerId: Optional[PyObjectId] = None
    partNumber: Optional[str] = Field(None, max_length=50)
    drawingNumber: Optional[str] = Field(None, max_length=50)
    imageUrl: Optional[str] = None
    isActive: Optional[bool] = None
    
    @validator('model')
    def validate_model(cls, v):
        if v and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Model must contain only alphanumeric characters, hyphens, and underscores')
        return v

class FittingTypeResponse(FittingTypeBase):
    """Fitting type response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    status: str
    category: Optional[FittingCategoryResponse] = None
    manufacturer: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class FittingCategoryListParams(BaseModel):
    """Fitting category list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    status: Optional[str] = None
    isActive: Optional[bool] = None
    sortBy: Optional[str] = Field("name")
    sortOrder: str = Field("asc", pattern="^(asc|desc)$")

class FittingTypeListParams(BaseModel):
    """Fitting type list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    categoryId: Optional[PyObjectId] = None
    manufacturerId: Optional[PyObjectId] = None
    status: Optional[str] = None
    isActive: Optional[bool] = None
    sortBy: Optional[str] = Field("name")
    sortOrder: str = Field("asc", pattern="^(asc|desc)$")

class FittingCategoryStats(BaseModel):
    """Fitting category statistics model"""
    
    totalCategories: int
    activeCategories: int
    inactiveCategories: int
    categoriesBySpecification: dict
    averageWarrantyPeriod: float

class FittingTypeStats(BaseModel):
    """Fitting type statistics model"""
    
    totalTypes: int
    activeTypes: int
    inactiveTypes: int
    typesByCategory: dict
    typesByManufacturer: dict
