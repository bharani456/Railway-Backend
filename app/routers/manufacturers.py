"""
Manufacturer management router - Task 5: Vendor and Manufacturer Management
APIs: GET /api/manufacturers, POST /api/manufacturers
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional
from datetime import datetime
import structlog

from app.models.vendor import ManufacturerCreate, ManufacturerUpdate, ManufacturerResponse
from app.models.base import APIResponse, PaginatedResponse
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_manufacturers(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    isVerified: Optional[bool] = Query(None),
    sortBy: Optional[str] = Query("name"),
    sortOrder: str = Query("asc", pattern="^(asc|desc)$"),
    current_user: dict = Depends(verify_token)
):
    """Get manufacturers with pagination and filters"""
    try:
        if not check_permissions(current_user["role"], "manufacturers"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        query = {}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"code": {"$regex": search, "$options": "i"}},
                {"licenseNumber": {"$regex": search, "$options": "i"}}
            ]
        if status:
            query["status"] = status
        if city:
            query["city"] = {"$regex": city, "$options": "i"}
        if state:
            query["state"] = {"$regex": state, "$options": "i"}
        if isVerified is not None:
            query["isVerified"] = isVerified
        
        manufacturers_collection = get_collection("manufacturers")
        skip = (page - 1) * limit
        sort_direction = 1 if sortOrder == "asc" else -1
        
        total = await manufacturers_collection.count_documents(query)
        cursor = manufacturers_collection.find(query).sort(sortBy, sort_direction).skip(skip).limit(limit)
        manufacturers = await cursor.to_list(length=limit)
        
        manufacturer_list = []
        for manufacturer in manufacturers:
            manufacturer_dict = dict(manufacturer)
            manufacturer_dict["id"] = str(manufacturer["_id"])
            manufacturer_list.append(manufacturer_dict)
        
        pages = (total + limit - 1) // limit
        
        return PaginatedResponse(
            data=manufacturer_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get manufacturers", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve manufacturers")

@router.post("", response_model=APIResponse)
async def create_manufacturer(
    manufacturer_data: ManufacturerCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """Create a new manufacturer"""
    try:
        if not check_permissions(current_user["role"], "manufacturers"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        manufacturers_collection = get_collection("manufacturers")
        
        # Check if code already exists
        existing_manufacturer = await manufacturers_collection.find_one({"code": manufacturer_data.code})
        if existing_manufacturer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Manufacturer code already exists")
        
        manufacturer_doc = {
            "name": manufacturer_data.name,
            "code": manufacturer_data.code,
            "contactInfo": manufacturer_data.contactInfo.dict(),
            "address": manufacturer_data.address,
            "city": manufacturer_data.city,
            "state": manufacturer_data.state,
            "pincode": manufacturer_data.pincode,
            "country": manufacturer_data.country,
            "website": manufacturer_data.website,
            "licenseNumber": manufacturer_data.licenseNumber,
            "licenseExpiry": manufacturer_data.licenseExpiry,
            "certificationNumber": manufacturer_data.certificationNumber,
            "certificationExpiry": manufacturer_data.certificationExpiry,
            "rating": manufacturer_data.rating,
            "isVerified": manufacturer_data.isVerified,
            "specializations": manufacturer_data.specializations or [],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": current_user["userId"],
            "status": "active"
        }
        
        result = await manufacturers_collection.insert_one(manufacturer_doc)
        created_manufacturer = await manufacturers_collection.find_one({"_id": result.inserted_id})
        created_manufacturer_dict = dict(created_manufacturer)
        created_manufacturer_dict["id"] = str(created_manufacturer["_id"])
        
        return APIResponse(success=True, data={"manufacturer": created_manufacturer_dict})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create manufacturer", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create manufacturer")
