"""
Installation tracking router - Task 9: Installation and Tracking System
APIs: POST /api/installations, GET /api/installations, PUT /api/installations/:id/status
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional, List, Dict, Any
from datetime import datetime
import structlog

from app.models.base import APIResponse, PaginatedResponse, Coordinates
from app.utils.security import verify_token, check_permissions, validate_gps_coordinates
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.post("", response_model=APIResponse)
async def create_installation(
    installation_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Create installation record
    
    Input: {"qrCodeId": "qr_code_id", "zoneId": "zone_id", "trackSection": "Section A-1", "kilometerPost": "KM 10.5", "installationCoordinates": {"lat": 13.0827, "lng": 80.2707}}
    Output: {"success": true, "data": {"installation": {...createdInstallationObject}}}
    """
    try:
        if not check_permissions(current_user["role"], "installations"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        qr_code_id = installation_data.get("qrCodeId")
        zone_id = installation_data.get("zoneId")
        track_section = installation_data.get("trackSection")
        kilometer_post = installation_data.get("kilometerPost")
        installation_coordinates = installation_data.get("installationCoordinates")
        
        if not qr_code_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QR code ID is required")
        
        if not zone_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Zone ID is required")
        
        if not track_section:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Track section is required")
        
        # Validate GPS coordinates
        if installation_coordinates:
            lat = installation_coordinates.get("lat")
            lng = installation_coordinates.get("lng")
            if not validate_gps_coordinates(lat, lng):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid GPS coordinates")
        
        # Verify QR code exists
        qr_codes_collection = get_collection("qr_codes")
        qr_code = await qr_codes_collection.find_one({"_id": qr_code_id})
        if not qr_code:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR code not found")
        
        # Check if QR code is already installed
        installations_collection = get_collection("fitting_installations")
        existing_installation = await installations_collection.find_one({"qrCodeId": qr_code_id})
        if existing_installation:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QR code is already installed")
        
        # Create installation record
        installation_doc = {
            "qrCodeId": qr_code_id,
            "zoneId": zone_id,
            "divisionId": installation_data.get("divisionId"),
            "stationId": installation_data.get("stationId"),
            "trackSection": track_section,
            "kilometerPost": kilometer_post,
            "installationCoordinates": installation_coordinates,
            "installationDate": datetime.utcnow(),
            "installedBy": current_user["userId"],
            "status": "installed",
            "warrantyStartDate": datetime.utcnow(),
            "warrantyEndDate": datetime.utcnow().replace(year=datetime.utcnow().year + 2),
            "remarks": installation_data.get("remarks"),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await installations_collection.insert_one(installation_doc)
        
        # Update QR code status
        await qr_codes_collection.update_one(
            {"_id": qr_code_id},
            {
                "$set": {
                    "status": "installed",
                    "installedAt": datetime.utcnow(),
                    "installedBy": current_user["userId"],
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        # Get created installation
        created_installation = await installations_collection.find_one({"_id": result.inserted_id})
        installation_dict = {k: v for k, v in created_installation.items() if k != "_id"}
        installation_dict["id"] = str(created_installation["_id"])
        
        logger.info(
            "Installation created successfully",
            user_id=current_user["userId"],
            qr_code_id=qr_code_id,
            track_section=track_section
        )
        
        return APIResponse(
            success=True,
            data={"installation": installation_dict}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create installation", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create installation")

@router.get("", response_model=PaginatedResponse)
async def get_installations(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    zoneId: Optional[str] = Query(None),
    divisionId: Optional[str] = Query(None),
    stationId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    trackSection: Optional[str] = Query(None),
    current_user: dict = Depends(verify_token)
):
    """
    Get installations with filters
    
    Input: Query params (zoneId="zone_id", divisionId="div_id", stationId="station_id", status="installed", trackSection="A-1")
    Output: {"success": true, "data": {"installations": [...], "pagination": {...}}}
    """
    try:
        if not check_permissions(current_user["role"], "installations"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Build query
        query = {}
        
        if zoneId:
            query["zoneId"] = zoneId
        if divisionId:
            query["divisionId"] = divisionId
        if stationId:
            query["stationId"] = stationId
        if status:
            query["status"] = status
        if trackSection:
            query["trackSection"] = {"$regex": trackSection, "$options": "i"}
        
        installations_collection = get_collection("fitting_installations")
        skip = (page - 1) * limit
        
        total = await installations_collection.count_documents(query)
        cursor = installations_collection.find(query).sort("installationDate", -1).skip(skip).limit(limit)
        installations = await cursor.to_list(length=limit)
        
        installation_list = []
        for installation in installations:
            installation_dict = {k: v for k, v in installation.items() if k != "_id"}
            installation_dict["id"] = str(installation["_id"])
            installation_list.append(installation_dict)
        
        pages = (total + limit - 1) // limit
        
        logger.info(
            "Installations retrieved successfully",
            user_id=current_user["userId"],
            total=total,
            page=page
        )
        
        return PaginatedResponse(
            data=installation_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get installations", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve installations")

@router.put("/{installation_id}/status", response_model=APIResponse)
async def update_installation_status(
    installation_id: str,
    status_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Update installation status
    
    Input: {"status": "maintenance_due", "remarks": "Routine maintenance required"}
    Output: {"success": true, "data": {"installation": {...updatedInstallationObject}}}
    """
    try:
        if not check_permissions(current_user["role"], "installations"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        new_status = status_data.get("status")
        remarks = status_data.get("remarks")
        
        if not new_status:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status is required")
        
        valid_statuses = ["installed", "in_service", "maintenance_due", "replaced", "retired"]
        if new_status not in valid_statuses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status. Valid options: {valid_statuses}")
        
        installations_collection = get_collection("fitting_installations")
        
        # Check if installation exists
        installation = await installations_collection.find_one({"_id": installation_id})
        if not installation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Installation not found")
        
        # Update installation status
        update_data = {
            "status": new_status,
            "updatedAt": datetime.utcnow(),
            "updatedBy": current_user["userId"]
        }
        
        if remarks:
            update_data["remarks"] = remarks
        
        if new_status == "replaced":
            update_data["replacedAt"] = datetime.utcnow()
            update_data["replacedBy"] = current_user["userId"]
        elif new_status == "retired":
            update_data["retiredAt"] = datetime.utcnow()
            update_data["retiredBy"] = current_user["userId"]
        
        await installations_collection.update_one(
            {"_id": installation_id},
            {"$set": update_data}
        )
        
        # Update QR code status
        qr_codes_collection = get_collection("qr_codes")
        await qr_codes_collection.update_one(
            {"_id": installation["qrCodeId"]},
            {
                "$set": {
                    "status": new_status,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        # Get updated installation
        updated_installation = await installations_collection.find_one({"_id": installation_id})
        installation_dict = {k: v for k, v in updated_installation.items() if k != "_id"}
        installation_dict["id"] = str(updated_installation["_id"])
        
        logger.info(
            "Installation status updated",
            user_id=current_user["userId"],
            installation_id=installation_id,
            new_status=new_status
        )
        
        return APIResponse(
            success=True,
            data={"installation": installation_dict}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update installation status", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update installation status")