"""
Division management router - Task 4: User and Hierarchy Management APIs
APIs: GET /api/divisions, POST /api/divisions
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional
from datetime import datetime
import structlog

from app.models.hierarchy import DivisionCreate, DivisionUpdate, DivisionResponse
from app.models.base import APIResponse, PaginatedResponse
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_divisions(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    zoneId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sortBy: Optional[str] = Query("name"),
    sortOrder: str = Query("asc", regex="^(asc|desc)$"),
    current_user: dict = Depends(verify_token)
):
    """Get divisions with pagination and filters"""
    try:
        if not check_permissions(current_user["role"], "divisions"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        query = {}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"code": {"$regex": search, "$options": "i"}}
            ]
        if zoneId:
            query["zoneId"] = zoneId
        if status:
            query["status"] = status
        
        divisions_collection = get_collection("divisions")
        skip = (page - 1) * limit
        sort_direction = 1 if sortOrder == "asc" else -1
        
        total = await divisions_collection.count_documents(query)
        cursor = divisions_collection.find(query).sort(sortBy, sort_direction).skip(skip).limit(limit)
        divisions = await cursor.to_list(length=limit)
        
        division_list = []
        for division in divisions:
            division_dict = dict(division)
            division_dict["id"] = str(division["_id"])
            division_list.append(division_dict)
        
        pages = (total + limit - 1) // limit
        
        return PaginatedResponse(
            data=division_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get divisions", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve divisions")

@router.post("", response_model=APIResponse)
async def create_division(
    division_data: DivisionCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """Create a new division"""
    try:
        if not check_permissions(current_user["role"], "divisions"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        divisions_collection = get_collection("divisions")
        
        existing_division = await divisions_collection.find_one({"code": division_data.code})
        if existing_division:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Division code already exists")
        
        division_doc = {
            "name": division_data.name,
            "code": division_data.code,
            "zoneId": division_data.zoneId,
            "description": division_data.description,
            "headquarters": division_data.headquarters,
            "coordinates": division_data.coordinates.dict() if division_data.coordinates else None,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": current_user["userId"],
            "status": "active"
        }
        
        result = await divisions_collection.insert_one(division_doc)
        created_division = await divisions_collection.find_one({"_id": result.inserted_id})
        created_division_dict = dict(created_division)
        created_division_dict["id"] = str(created_division["_id"])
        
        return APIResponse(success=True, data={"division": created_division_dict})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create division", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create division")
