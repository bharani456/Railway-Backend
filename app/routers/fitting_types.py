"""
Fitting types router - Task 6: Fitting Management System
APIs: GET /api/fitting-types, POST /api/fitting-types
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional
from datetime import datetime
import structlog

from app.models.fitting import FittingTypeCreate, FittingTypeUpdate, FittingTypeResponse
from app.models.base import APIResponse, PaginatedResponse
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_fitting_types(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    categoryId: Optional[str] = Query(None),
    manufacturerId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    isActive: Optional[bool] = Query(None),
    sortBy: Optional[str] = Query("name"),
    sortOrder: str = Query("asc", regex="^(asc|desc)$"),
    current_user: dict = Depends(verify_token)
):
    """Get fitting types with pagination and filters"""
    try:
        if not check_permissions(current_user["role"], "fitting_types"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        query = {}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"model": {"$regex": search, "$options": "i"}},
                {"partNumber": {"$regex": search, "$options": "i"}}
            ]
        if categoryId:
            query["categoryId"] = categoryId
        if manufacturerId:
            query["manufacturerId"] = manufacturerId
        if status:
            query["status"] = status
        if isActive is not None:
            query["isActive"] = isActive
        
        types_collection = get_collection("fitting_types")
        skip = (page - 1) * limit
        sort_direction = 1 if sortOrder == "asc" else -1
        
        total = await types_collection.count_documents(query)
        cursor = types_collection.find(query).sort(sortBy, sort_direction).skip(skip).limit(limit)
        types = await cursor.to_list(length=limit)
        
        type_list = []
        for fitting_type in types:
            type_dict = dict(fitting_type)
            type_dict["id"] = str(fitting_type["_id"])
            type_list.append(type_dict)
        
        pages = (total + limit - 1) // limit
        
        return PaginatedResponse(
            data=type_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get fitting types", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve fitting types")

@router.post("", response_model=APIResponse)
async def create_fitting_type(
    type_data: FittingTypeCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """Create a new fitting type"""
    try:
        if not check_permissions(current_user["role"], "fitting_types"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        types_collection = get_collection("fitting_types")
        
        type_doc = {
            "name": type_data.name,
            "model": type_data.model,
            "categoryId": type_data.categoryId,
            "description": type_data.description,
            "specifications": type_data.specifications.dict() if type_data.specifications else None,
            "manufacturerId": type_data.manufacturerId,
            "partNumber": type_data.partNumber,
            "drawingNumber": type_data.drawingNumber,
            "imageUrl": type_data.imageUrl,
            "isActive": type_data.isActive,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": current_user["userId"],
            "status": "active"
        }
        
        result = await types_collection.insert_one(type_doc)
        created_type = await types_collection.find_one({"_id": result.inserted_id})
        created_type_dict = dict(created_type)
        created_type_dict["id"] = str(created_type["_id"])
        
        return APIResponse(success=True, data={"fittingType": created_type_dict})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create fitting type", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create fitting type")
