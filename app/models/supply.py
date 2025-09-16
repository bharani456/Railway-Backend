"""
Supply order and batch models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from decimal import Decimal

from app.models.base import BaseDocument, PyObjectId

class SupplyOrderItem(BaseModel):
    """Supply order item model"""
    
    fittingTypeId: PyObjectId
    quantity: int = Field(..., ge=1)
    unitPrice: Decimal = Field(..., ge=0)
    totalPrice: Decimal = Field(..., ge=0)
    specifications: Optional[Dict[str, Any]] = None
    deliveryDate: Optional[datetime] = None
    remarks: Optional[str] = None

class SupplyOrderBase(BaseModel):
    """Base supply order model"""
    
    orderNumber: str = Field(..., min_length=5, max_length=50)
    vendorId: PyObjectId
    manufacturerId: Optional[PyObjectId] = None
    orderDate: datetime = Field(default_factory=datetime.utcnow)
    expectedDeliveryDate: Optional[datetime] = None
    actualDeliveryDate: Optional[datetime] = None
    items: List[SupplyOrderItem] = Field(..., min_items=1)
    totalAmount: Decimal = Field(..., ge=0)
    currency: str = Field(default="INR", max_length=3)
    status: str = Field(default="pending")
    priority: str = Field(default="normal")
    remarks: Optional[str] = None
    purchaseOrderNumber: Optional[str] = Field(None, max_length=50)
    
    @validator('orderNumber')
    def validate_order_number(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Order number must contain only alphanumeric characters, hyphens, and underscores')
        return v

class SupplyOrderCreate(SupplyOrderBase):
    """Supply order creation model"""
    
    pass

class SupplyOrderUpdate(BaseModel):
    """Supply order update model"""
    
    expectedDeliveryDate: Optional[datetime] = None
    actualDeliveryDate: Optional[datetime] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    remarks: Optional[str] = None
    purchaseOrderNumber: Optional[str] = Field(None, max_length=50)

class SupplyOrderResponse(SupplyOrderBase):
    """Supply order response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    vendor: Optional[Dict[str, Any]] = None
    manufacturer: Optional[Dict[str, Any]] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class FittingBatchBase(BaseModel):
    """Base fitting batch model"""
    
    batchNumber: str = Field(..., min_length=5, max_length=50)
    supplyOrderId: PyObjectId
    supplyOrderItemIndex: int = Field(..., ge=0)
    manufacturerId: PyObjectId
    quantity: int = Field(..., ge=1)
    manufacturingDate: datetime = Field(default_factory=datetime.utcnow)
    expiryDate: Optional[datetime] = None
    status: str = Field(default="manufactured")
    qualityGrade: Optional[str] = None
    testResults: Optional[Dict[str, Any]] = None
    qualityDocuments: Optional[List[str]] = []
    remarks: Optional[str] = None
    
    @validator('batchNumber')
    def validate_batch_number(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Batch number must contain only alphanumeric characters, hyphens, and underscores')
        return v

class FittingBatchCreate(FittingBatchBase):
    """Fitting batch creation model"""
    
    pass

class FittingBatchUpdate(BaseModel):
    """Fitting batch update model"""
    
    status: Optional[str] = None
    qualityGrade: Optional[str] = None
    testResults: Optional[Dict[str, Any]] = None
    qualityDocuments: Optional[List[str]] = None
    remarks: Optional[str] = None

class FittingBatchResponse(FittingBatchBase):
    """Fitting batch response model"""
    
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[PyObjectId] = None
    updatedBy: Optional[PyObjectId] = None
    supplyOrder: Optional[Dict[str, Any]] = None
    manufacturer: Optional[Dict[str, Any]] = None
    qrCodeCount: Optional[int] = 0
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SupplyOrderListParams(BaseModel):
    """Supply order list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    status: Optional[str] = None
    vendorId: Optional[PyObjectId] = None
    manufacturerId: Optional[PyObjectId] = None
    dateRange: Optional[str] = None
    sortBy: Optional[str] = Field("orderDate")
    sortOrder: str = Field("desc", regex="^(asc|desc)$")

class FittingBatchListParams(BaseModel):
    """Fitting batch list parameters"""
    
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    status: Optional[str] = None
    supplyOrderId: Optional[PyObjectId] = None
    manufacturerId: Optional[PyObjectId] = None
    dateRange: Optional[str] = None
    sortBy: Optional[str] = Field("manufacturingDate")
    sortOrder: str = Field("desc", regex="^(asc|desc)$")

class SupplyOrderStats(BaseModel):
    """Supply order statistics model"""
    
    totalOrders: int
    pendingOrders: int
    completedOrders: int
    cancelledOrders: int
    totalValue: Decimal
    averageOrderValue: Decimal
    ordersByStatus: Dict[str, int]
    ordersByVendor: Dict[str, int]

class FittingBatchStats(BaseModel):
    """Fitting batch statistics model"""
    
    totalBatches: int
    manufacturedBatches: int
    qualityCheckedBatches: int
    rejectedBatches: int
    totalQuantity: int
    averageBatchSize: float
    batchesByStatus: Dict[str, int]
    batchesByManufacturer: Dict[str, int]
