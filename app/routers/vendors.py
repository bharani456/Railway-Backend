"""
Vendor management router - Task 5: Vendor and Manufacturer Management
APIs: GET /api/vendors, POST /api/vendors
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional
from datetime import datetime
import structlog

from app.models.vendor import VendorCreate, VendorUpdate, VendorResponse
from app.models.base import APIResponse, PaginatedResponse
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_vendors(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    isVerified: Optional[bool] = Query(None),
    sortBy: Optional[str] = Query("name"),
    sortOrder: str = Query("asc", regex="^(asc|desc)$"),
    current_user: dict = Depends(verify_token)
):
    """Get vendors with pagination and filters"""
    try:
        if not check_permissions(current_user["role"], "vendors"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        query = {}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"code": {"$regex": search, "$options": "i"}},
                {"gstNumber": {"$regex": search, "$options": "i"}}
            ]
        if status:
            query["status"] = status
        if city:
            query["city"] = {"$regex": city, "$options": "i"}
        if state:
            query["state"] = {"$regex": state, "$options": "i"}
        if isVerified is not None:
            query["isVerified"] = isVerified
        
        vendors_collection = get_collection("vendors")
        skip = (page - 1) * limit
        sort_direction = 1 if sortOrder == "asc" else -1
        
        total = await vendors_collection.count_documents(query)
        cursor = vendors_collection.find(query).sort(sortBy, sort_direction).skip(skip).limit(limit)
        vendors = await cursor.to_list(length=limit)
        
        vendor_list = []
        for vendor in vendors:
            vendor_dict = dict(vendor)
            vendor_dict["id"] = str(vendor["_id"])
            vendor_list.append(vendor_dict)
        
        pages = (total + limit - 1) // limit
        
        return PaginatedResponse(
            data=vendor_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get vendors", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve vendors")

@router.post("", response_model=APIResponse)
async def create_vendor(
    vendor_data: VendorCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """Create a new vendor"""
    try:
        if not check_permissions(current_user["role"], "vendors"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        vendors_collection = get_collection("vendors")
        
        # Check if GST number already exists
        if vendor_data.gstNumber:
            existing_vendor = await vendors_collection.find_one({"gstNumber": vendor_data.gstNumber})
            if existing_vendor:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GST number already exists")
        
        vendor_doc = {
            "name": vendor_data.name,
            "code": vendor_data.code,
            "gstNumber": vendor_data.gstNumber,
            "panNumber": vendor_data.panNumber,
            "contactInfo": vendor_data.contactInfo.dict(),
            "address": vendor_data.address,
            "city": vendor_data.city,
            "state": vendor_data.state,
            "pincode": vendor_data.pincode,
            "country": vendor_data.country,
            "website": vendor_data.website,
            "registrationDate": vendor_data.registrationDate or datetime.utcnow(),
            "licenseNumber": vendor_data.licenseNumber,
            "licenseExpiry": vendor_data.licenseExpiry,
            "rating": vendor_data.rating,
            "isVerified": vendor_data.isVerified,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": current_user["userId"],
            "status": "active"
        }
        
        result = await vendors_collection.insert_one(vendor_doc)
        created_vendor = await vendors_collection.find_one({"_id": result.inserted_id})
        created_vendor_dict = dict(created_vendor)
        created_vendor_dict["id"] = str(created_vendor["_id"])
        
        return APIResponse(success=True, data={"vendor": created_vendor_dict})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create vendor", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create vendor")
