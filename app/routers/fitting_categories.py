"""
Fitting categories router - Task 6: Fitting Management System
APIs: GET /api/fitting-categories, POST /api/fitting-categories
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional
from datetime import datetime
import structlog

from app.models.fitting import FittingCategoryCreate, FittingCategoryUpdate, FittingCategoryResponse
from app.models.base import APIResponse, PaginatedResponse
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_fitting_categories(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    isActive: Optional[bool] = Query(None),
    sortBy: Optional[str] = Query("name"),
    sortOrder: str = Query("asc", pattern="^(asc|desc)$"),
    current_user: dict = Depends(verify_token)
):
    """Get fitting categories with pagination and filters"""
    try:
        if not check_permissions(current_user["role"], "fitting_categories"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        query = {}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"code": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        if status:
            query["status"] = status
        if isActive is not None:
            query["isActive"] = isActive
        
        categories_collection = get_collection("fitting_categories")
        skip = (page - 1) * limit
        sort_direction = 1 if sortOrder == "asc" else -1
        
        total = await categories_collection.count_documents(query)
        cursor = categories_collection.find(query).sort(sortBy, sort_direction).skip(skip).limit(limit)
        categories = await cursor.to_list(length=limit)
        
        category_list = []
        for category in categories:
            category_dict = dict(category)
            category_dict["id"] = str(category["_id"])
            category_list.append(category_dict)
        
        pages = (total + limit - 1) // limit
        
        return PaginatedResponse(
            data=category_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get fitting categories", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve fitting categories")

@router.post("", response_model=APIResponse)
async def create_fitting_category(
    category_data: FittingCategoryCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """Create a new fitting category"""
    try:
        if not check_permissions(current_user["role"], "fitting_categories"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        categories_collection = get_collection("fitting_categories")
        
        # Check if code already exists
        existing_category = await categories_collection.find_one({"code": category_data.code})
        if existing_category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category code already exists")
        
        category_doc = {
            "name": category_data.name,
            "code": category_data.code,
            "description": category_data.description,
            "specifications": category_data.specifications.dict() if category_data.specifications else None,
            "warrantyPeriodMonths": category_data.warrantyPeriodMonths,
            "standardCode": category_data.standardCode,
            "drawingNumber": category_data.drawingNumber,
            "imageUrl": category_data.imageUrl,
            "isActive": category_data.isActive,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": current_user["userId"],
            "status": "active"
        }
        
        result = await categories_collection.insert_one(category_doc)
        created_category = await categories_collection.find_one({"_id": result.inserted_id})
        created_category_dict = dict(created_category)
        created_category_dict["id"] = str(created_category["_id"])
        
        return APIResponse(success=True, data={"category": created_category_dict})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create fitting category", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create fitting category")
