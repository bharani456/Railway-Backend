"""
Hierarchy models for zones, divisions, and stations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.models.base import BaseDocument, Coordinates, PyObjectId

class ZoneBase(BaseModel):
    """Base zone model"""
    
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=10)
    description: Optional[str] = Field(None, max_length=500)
    headquarters: Optional[str] = Field(None, max_length=100)
    coordinates: Optional[Coordinates] = None
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isupper():
            raise ValueError('Zone code must be uppercase')
        return v

class ZoneCreate(ZoneBase):
    """Zone creation model"""
    
    pass

class ZoneUpdate(BaseModel):
    """Zone update model"""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=10)
    description: Optional[str] = Field(None, max_length=500)
    headquarters: Optional[str] = Field(None, max_length=100)
    coordinates: Optional[Coordinates] = None
    
    @validator('code')
    def validate_code(cls, v):
        if v and not v.isupper():
            raise ValueError('Zone code must be uppercase')
        return v

class ZoneResponse(ZoneBase):
    """Zone response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    status: str
    divisionCount: Optional[int] = 0
    stationCount: Optional[int] = 0
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class DivisionBase(BaseModel):
    """Base division model"""
    
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=10)
    zoneId: PyObjectId
    description: Optional[str] = Field(None, max_length=500)
    headquarters: Optional[str] = Field(None, max_length=100)
    coordinates: Optional[Coordinates] = None
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isupper():
            raise ValueError('Division code must be uppercase')
        return v

class DivisionCreate(DivisionBase):
    """Division creation model"""
    
    pass

class DivisionUpdate(BaseModel):
    """Division update model"""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=10)
    zoneId: Optional[PyObjectId] = None
    description: Optional[str] = Field(None, max_length=500)
    headquarters: Optional[str] = Field(None, max_length=100)
    coordinates: Optional[Coordinates] = None
    
    @validator('code')
    def validate_code(cls, v):
        if v and not v.isupper():
            raise ValueError('Division code must be uppercase')
        return v

class DivisionResponse(DivisionBase):
    """Division response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    status: str
    zone: Optional[ZoneResponse] = None
    stationCount: Optional[int] = 0
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class StationBase(BaseModel):
    """Base station model"""
    
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=10)
    divisionId: PyObjectId
    description: Optional[str] = Field(None, max_length=500)
    stationType: Optional[str] = Field(None, max_length=50)
    coordinates: Optional[Coordinates] = None
    platformCount: Optional[int] = Field(None, ge=0)
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isupper():
            raise ValueError('Station code must be uppercase')
        return v

class StationCreate(StationBase):
    """Station creation model"""
    
    pass

class StationUpdate(BaseModel):
    """Station update model"""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=10)
    divisionId: Optional[PyObjectId] = None
    description: Optional[str] = Field(None, max_length=500)
    stationType: Optional[str] = Field(None, max_length=50)
    coordinates: Optional[Coordinates] = None
    platformCount: Optional[int] = Field(None, ge=0)
    
    @validator('code')
    def validate_code(cls, v):
        if v and not v.isupper():
            raise ValueError('Station code must be uppercase')
        return v

class StationResponse(StationBase):
    """Station response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    status: str
    division: Optional[DivisionResponse] = None
    zone: Optional[ZoneResponse] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class HierarchyResponse(BaseModel):
    """Hierarchy response model"""
    
    zones: List[ZoneResponse]
    divisions: List[DivisionResponse]
    stations: List[StationResponse]

class ZoneListParams(BaseModel):
    """Zone list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    status: Optional[str] = None
    sortBy: Optional[str] = Field("name")
    sortOrder: str = Field("asc", pattern="^(asc|desc)$")

class DivisionListParams(BaseModel):
    """Division list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    zoneId: Optional[PyObjectId] = None
    status: Optional[str] = None
    sortBy: Optional[str] = Field("name")
    sortOrder: str = Field("asc", pattern="^(asc|desc)$")

class StationListParams(BaseModel):
    """Station list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    zoneId: Optional[PyObjectId] = None
    divisionId: Optional[PyObjectId] = None
    status: Optional[str] = None
    sortBy: Optional[str] = Field("name")
    sortOrder: str = Field("asc", pattern="^(asc|desc)$")

class ZoneStats(BaseModel):
    """Zone statistics model"""
    
    totalZones: int
    activeZones: int
    inactiveZones: int
    zonesByRegion: dict
    averageDivisionsPerZone: float

class DivisionStats(BaseModel):
    """Division statistics model"""
    
    totalDivisions: int
    activeDivisions: int
    inactiveDivisions: int
    divisionsByZone: dict
    averageStationsPerDivision: float

class StationStats(BaseModel):
    """Station statistics model"""
    
    totalStations: int
    activeStations: int
    inactiveStations: int
    stationsByDivision: dict
    stationsByType: dict
