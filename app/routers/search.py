"""
Search router - Task 15: Notification and Search Systems
APIs: GET /api/search/fittings, GET /api/search/locations
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional, List, Dict, Any
from datetime import datetime
import structlog

from app.models.base import APIResponse, PaginatedResponse
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("/fittings", response_model=APIResponse)
async def search_fittings(
    request: Request,
    query: str = Query(..., description="Search query"),
    filters: Optional[str] = Query(None, description="JSON string of filters"),
    sort: str = Query("relevance", description="Sort by: relevance, date, name"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(verify_token)
):
    """
    Search fittings
    
    Input: Query params (query="rail clip", filters={"fittingType": "elastic_rail_clip", "status": "in_service"}, sort="relevance")
    Output: {"success": true, "data": {"results": [...], "pagination": {...}, "facets": {...}}}
    """
    try:
        if not check_permissions(current_user["role"], "search"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Parse filters
        filter_dict = {}
        if filters:
            import json
            try:
                filter_dict = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filters format")
        
        # Build search query
        search_query = {
            "$or": [
                {"qrCode": {"$regex": query, "$options": "i"}},
                {"fittingTypeName": {"$regex": query, "$options": "i"}},
                {"trackSection": {"$regex": query, "$options": "i"}},
                {"stationName": {"$regex": query, "$options": "i"}}
            ]
        }
        
        # Apply filters
        if filter_dict.get("fittingType"):
            search_query["fittingType"] = filter_dict["fittingType"]
        if filter_dict.get("status"):
            search_query["status"] = filter_dict["status"]
        if filter_dict.get("zoneId"):
            search_query["zoneId"] = filter_dict["zoneId"]
        if filter_dict.get("divisionId"):
            search_query["divisionId"] = filter_dict["divisionId"]
        if filter_dict.get("stationId"):
            search_query["stationId"] = filter_dict["stationId"]
        
        # Mock search results
        results = [
            {
                "type": "qr_code",
                "qrCode": "QRTF_123456_000001_ABC123",
                "fittingType": "Elastic Rail Clip",
                "model": "ERC-A100",
                "location": "Chennai Central, Track 1",
                "status": "in_service",
                "relevanceScore": 0.95,
                "lastInspection": "2025-09-01",
                "nextInspection": "2025-12-01"
            },
            {
                "type": "qr_code",
                "qrCode": "QRTF_123456_000002_DEF456",
                "fittingType": "Rail Pad",
                "model": "RP-B200",
                "location": "Chennai Central, Track 2",
                "status": "in_service",
                "relevanceScore": 0.87,
                "lastInspection": "2025-08-15",
                "nextInspection": "2025-11-15"
            }
        ]
        
        # Mock facets
        facets = {
            "fittingTypes": [
                {"value": "elastic_rail_clip", "count": 1500},
                {"value": "rail_pad", "count": 800},
                {"value": "liner", "count": 1200}
            ],
            "locations": [
                {"value": "Chennai Central", "count": 500},
                {"value": "Madurai Junction", "count": 300},
                {"value": "Coimbatore", "count": 200}
            ],
            "statuses": [
                {"value": "in_service", "count": 2000},
                {"value": "maintenance_due", "count": 150},
                {"value": "replaced", "count": 50}
            ]
        }
        
        # Calculate pagination
        total = len(results)
        pages = (total + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_results = results[start_idx:end_idx]
        
        logger.info(
            "Fittings search completed",
            user_id=current_user["userId"],
            query=query,
            results_count=len(paginated_results)
        )
        
        return APIResponse(
            success=True,
            data={
                "results": paginated_results,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": pages,
                    "hasNext": page < pages,
                    "hasPrev": page > 1
                },
                "facets": facets
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to search fittings", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search fittings")

@router.get("/locations", response_model=APIResponse)
async def search_locations(
    request: Request,
    query: str = Query(..., description="Search query"),
    type: Optional[str] = Query(None, description="Location type: zone, division, station"),
    current_user: dict = Depends(verify_token)
):
    """
    Search locations
    
    Input: Query params (query="chennai", type="station")
    Output: {"success": true, "data": {"locations": [...]}}
    """
    try:
        if not check_permissions(current_user["role"], "search"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Build search query based on type
        if type == "zone":
            collection_name = "zones"
            search_fields = ["name", "code"]
        elif type == "division":
            collection_name = "divisions"
            search_fields = ["name", "code"]
        elif type == "station":
            collection_name = "stations"
            search_fields = ["name", "code"]
        else:
            # Search all location types
            collection_name = None
            search_fields = ["name", "code"]
        
        # Mock location search results
        locations = [
            {
                "id": "zone_001",
                "name": "Chennai Central",
                "type": "station",
                "code": "MAS",
                "hierarchy": "Southern Railway > Chennai Division > Chennai Central",
                "coordinates": {"lat": 13.0827, "lng": 80.2707}
            },
            {
                "id": "zone_002",
                "name": "Chennai Division",
                "type": "division",
                "code": "MDU",
                "hierarchy": "Southern Railway > Chennai Division",
                "coordinates": {"lat": 13.0827, "lng": 80.2707}
            },
            {
                "id": "zone_003",
                "name": "Chennai Egmore",
                "type": "station",
                "code": "MSB",
                "hierarchy": "Southern Railway > Chennai Division > Chennai Egmore",
                "coordinates": {"lat": 13.0827, "lng": 80.2707}
            }
        ]
        
        # Filter by type if specified
        if type:
            locations = [loc for loc in locations if loc["type"] == type]
        
        # Filter by query
        filtered_locations = []
        for location in locations:
            if any(query.lower() in location[field].lower() for field in search_fields):
                filtered_locations.append(location)
        
        logger.info(
            "Locations search completed",
            user_id=current_user["userId"],
            query=query,
            type=type,
            results_count=len(filtered_locations)
        )
        
        return APIResponse(
            success=True,
            data={"locations": filtered_locations}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to search locations", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search locations")