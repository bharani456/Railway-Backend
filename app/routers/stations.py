"""
Station management router - Task 4: User and Hierarchy Management APIs
APIs: GET /api/stations, POST /api/stations
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional
from datetime import datetime
import structlog

from app.models.hierarchy import StationCreate, StationUpdate, StationResponse
from app.models.base import APIResponse, PaginatedResponse
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_stations(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    zoneId: Optional[str] = Query(None),
    divisionId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sortBy: Optional[str] = Query("name"),
    sortOrder: str = Query("asc", regex="^(asc|desc)$"),
    current_user: dict = Depends(verify_token)
):
    """Get stations with pagination and filters"""
    try:
        if not check_permissions(current_user["role"], "stations"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        query = {}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"code": {"$regex": search, "$options": "i"}}
            ]
        if zoneId:
            query["zoneId"] = zoneId
        if divisionId:
            query["divisionId"] = divisionId
        if status:
            query["status"] = status
        
        stations_collection = get_collection("stations")
        skip = (page - 1) * limit
        sort_direction = 1 if sortOrder == "asc" else -1
        
        total = await stations_collection.count_documents(query)
        cursor = stations_collection.find(query).sort(sortBy, sort_direction).skip(skip).limit(limit)
        stations = await cursor.to_list(length=limit)
        
        station_list = []
        for station in stations:
            station_dict = dict(station)
            station_dict["id"] = str(station["_id"])
            station_list.append(station_dict)
        
        pages = (total + limit - 1) // limit
        
        return PaginatedResponse(
            data=station_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get stations", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve stations")

@router.post("", response_model=APIResponse)
async def create_station(
    station_data: StationCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """Create a new station"""
    try:
        if not check_permissions(current_user["role"], "stations"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        stations_collection = get_collection("stations")
        
        existing_station = await stations_collection.find_one({"code": station_data.code})
        if existing_station:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Station code already exists")
        
        station_doc = {
            "name": station_data.name,
            "code": station_data.code,
            "divisionId": station_data.divisionId,
            "description": station_data.description,
            "stationType": station_data.stationType,
            "coordinates": station_data.coordinates.dict() if station_data.coordinates else None,
            "platformCount": station_data.platformCount,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": current_user["userId"],
            "status": "active"
        }
        
        result = await stations_collection.insert_one(station_doc)
        created_station = await stations_collection.find_one({"_id": result.inserted_id})
        created_station_dict = dict(created_station)
        created_station_dict["id"] = str(created_station["_id"])
        
        return APIResponse(success=True, data={"station": created_station_dict})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create station", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create station")
