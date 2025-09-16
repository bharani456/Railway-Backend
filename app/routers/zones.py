"""
Zone management router - Task 4: User and Hierarchy Management APIs
APIs: GET /api/zones, POST /api/zones
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional, List
from datetime import datetime
import structlog

from app.models.hierarchy import (
    ZoneCreate, ZoneUpdate, ZoneResponse, ZoneListParams, ZoneStats
)
from app.models.base import APIResponse, PaginatedResponse
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_zones(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sortBy: Optional[str] = Query("name", description="Sort field"),
    sortOrder: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: dict = Depends(verify_token)
):
    """
    Get zones with pagination and filters
    
    Input: Query params (page=1, limit=10, search="southern", status="active")
    Output: {"success": true, "data": {"zones": [...], "pagination": {...}}}
    """
    try:
        # Check permissions
        if not check_permissions(current_user["role"], "zones"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Build query
        query = {}
        
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"code": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        if status:
            query["status"] = status
        
        # Get zones collection
        zones_collection = get_collection("zones")
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Build sort
        sort_direction = 1 if sortOrder == "asc" else -1
        sort_field = sortBy if sortBy in ["name", "code", "createdAt", "updatedAt"] else "name"
        
        # Get total count
        total = await zones_collection.count_documents(query)
        
        # Get zones
        cursor = zones_collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)
        zones = await cursor.to_list(length=limit)
        
        # Format response
        zone_list = []
        for zone in zones:
            zone_dict = dict(zone)
            zone_dict["id"] = str(zone["_id"])
            zone_list.append(zone_dict)
        
        # Calculate pagination info
        pages = (total + limit - 1) // limit
        
        logger.info(
            "Zones retrieved successfully",
            user_id=current_user["userId"],
            total=total,
            page=page,
            limit=limit
        )
        
        return PaginatedResponse(
            data=zone_list,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "pages": pages,
                "hasNext": page < pages,
                "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get zones", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve zones"
        )

@router.post("", response_model=APIResponse)
async def create_zone(
    zone_data: ZoneCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Create a new zone
    
    Input: {"name": "Southern Railway", "code": "SR", "description": "Southern Railway Zone"}
    Output: {"success": true, "data": {"zone": {...createdZoneObject}}}
    """
    try:
        # Check permissions
        if not check_permissions(current_user["role"], "zones"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Get zones collection
        zones_collection = get_collection("zones")
        
        # Check if code already exists
        existing_zone = await zones_collection.find_one({"code": zone_data.code})
        if existing_zone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Zone code already exists"
            )
        
        # Create zone document
        zone_doc = {
            "name": zone_data.name,
            "code": zone_data.code,
            "description": zone_data.description,
            "headquarters": zone_data.headquarters,
            "coordinates": zone_data.coordinates.dict() if zone_data.coordinates else None,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": current_user["userId"],
            "status": "active"
        }
        
        # Insert zone
        result = await zones_collection.insert_one(zone_doc)
        
        # Get created zone
        created_zone = await zones_collection.find_one({"_id": result.inserted_id})
        created_zone_dict = dict(created_zone)
        created_zone_dict["id"] = str(created_zone["_id"])
        
        logger.info(
            "Zone created successfully",
            user_id=current_user["userId"],
            created_zone_id=str(result.inserted_id),
            code=zone_data.code
        )
        
        return APIResponse(
            success=True,
            data={"zone": created_zone_dict}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create zone", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create zone"
        )

@router.put("/{zone_id}", response_model=APIResponse)
async def update_zone(
    zone_id: str,
    zone_data: ZoneUpdate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Update a zone
    
    Input: {"name": "Updated Zone Name", "description": "Updated description"}
    Output: {"success": true, "data": {"zone": {...updatedZoneObject}}}
    """
    try:
        # Check permissions
        if not check_permissions(current_user["role"], "zones"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Get zones collection
        zones_collection = get_collection("zones")
        
        # Check if zone exists
        existing_zone = await zones_collection.find_one({"_id": zone_id})
        if not existing_zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Zone not found"
            )
        
        # Check if code already exists (if being updated)
        if zone_data.code and zone_data.code != existing_zone["code"]:
            code_exists = await zones_collection.find_one({
                "code": zone_data.code,
                "_id": {"$ne": zone_id}
            })
            if code_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Zone code already exists"
                )
        
        # Build update data
        update_data = {k: v for k, v in zone_data.dict(exclude_unset=True).items() if v is not None}
        if zone_data.coordinates:
            update_data["coordinates"] = zone_data.coordinates.dict()
        update_data["updatedAt"] = datetime.utcnow()
        update_data["updatedBy"] = current_user["userId"]
        
        # Update zone
        await zones_collection.update_one(
            {"_id": zone_id},
            {"$set": update_data}
        )
        
        # Get updated zone
        updated_zone = await zones_collection.find_one({"_id": zone_id})
        updated_zone_dict = dict(updated_zone)
        updated_zone_dict["id"] = str(updated_zone["_id"])
        
        logger.info(
            "Zone updated successfully",
            user_id=current_user["userId"],
            updated_zone_id=zone_id
        )
        
        return APIResponse(
            success=True,
            data={"zone": updated_zone_dict}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update zone", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update zone"
        )

@router.delete("/{zone_id}", response_model=APIResponse)
async def delete_zone(
    zone_id: str,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Delete a zone (soft delete)
    
    Input: Zone ID in URL
    Output: {"success": true, "message": "Zone deleted successfully"}
    """
    try:
        # Check permissions
        if not check_permissions(current_user["role"], "zones"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Get zones collection
        zones_collection = get_collection("zones")
        
        # Check if zone exists
        existing_zone = await zones_collection.find_one({"_id": zone_id})
        if not existing_zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Zone not found"
            )
        
        # Check if zone has divisions
        divisions_collection = get_collection("divisions")
        division_count = await divisions_collection.count_documents({"zoneId": zone_id, "status": {"$ne": "deleted"}})
        if division_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete zone with existing divisions"
            )
        
        # Soft delete zone
        await zones_collection.update_one(
            {"_id": zone_id},
            {
                "$set": {
                    "status": "deleted",
                    "deletedAt": datetime.utcnow(),
                    "deletedBy": current_user["userId"],
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        logger.info(
            "Zone deleted successfully",
            user_id=current_user["userId"],
            deleted_zone_id=zone_id
        )
        
        return APIResponse(
            success=True,
            message="Zone deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete zone", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete zone"
        )

@router.get("/stats", response_model=APIResponse)
async def get_zone_stats(
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Get zone statistics
    """
    try:
        # Check permissions
        if not check_permissions(current_user["role"], "zones"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        zones_collection = get_collection("zones")
        divisions_collection = get_collection("divisions")
        stations_collection = get_collection("stations")
        
        # Get statistics
        total_zones = await zones_collection.count_documents({"status": {"$ne": "deleted"}})
        active_zones = await zones_collection.count_documents({"status": "active"})
        
        # Get zones with division and station counts
        zones = await zones_collection.find({"status": {"$ne": "deleted"}}).to_list(length=None)
        zone_stats = []
        
        for zone in zones:
            division_count = await divisions_collection.count_documents({
                "zoneId": zone["_id"],
                "status": {"$ne": "deleted"}
            })
            
            station_count = await stations_collection.count_documents({
                "zoneId": zone["_id"],
                "status": {"$ne": "deleted"}
            })
            
            zone_stats.append({
                "zoneId": str(zone["_id"]),
                "name": zone["name"],
                "code": zone["code"],
                "divisionCount": division_count,
                "stationCount": station_count
            })
        
        stats = {
            "totalZones": total_zones,
            "activeZones": active_zones,
            "zones": zone_stats
        }
        
        logger.info(
            "Zone stats retrieved successfully",
            user_id=current_user["userId"]
        )
        
        return APIResponse(
            success=True,
            data=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get zone stats", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve zone statistics"
        )
