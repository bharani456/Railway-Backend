"""
Maintenance management router - Task 11: Maintenance Management System
APIs: GET /api/maintenance-records, POST /api/maintenance-records, PUT /api/maintenance-records/:id/quality-check
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import structlog

from app.models.base import APIResponse, PaginatedResponse, MaintenanceType, MaintenanceStatus
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_maintenance_records(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    qrCodeId: Optional[str] = Query(None),
    performedBy: Optional[str] = Query(None),
    maintenanceType: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    dateRange: Optional[str] = Query(None),
    current_user: dict = Depends(verify_token)
):
    """
    Get maintenance records with filters
    
    Input: Query params (qrCodeId="qr_id", performedBy="user_id", maintenanceType="corrective", dateRange="2025-01-01,2025-12-31")
    Output: {"success": true, "data": {"maintenanceRecords": [...], "pagination": {...}}}
    """
    try:
        if not check_permissions(current_user["role"], "maintenance_records"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Build query
        query = {}
        
        if qrCodeId:
            query["qrCodeId"] = qrCodeId
        if performedBy:
            query["performedBy"] = performedBy
        if maintenanceType:
            query["maintenanceType"] = maintenanceType
        if status:
            query["status"] = status
        
        if dateRange:
            try:
                start_date, end_date = dateRange.split(",")
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                query["maintenanceDate"] = {"$gte": start_dt, "$lte": end_dt}
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date range format")
        
        maintenance_collection = get_collection("maintenance_records")
        skip = (page - 1) * limit
        
        total = await maintenance_collection.count_documents(query)
        cursor = maintenance_collection.find(query).sort("maintenanceDate", -1).skip(skip).limit(limit)
        maintenance_records = await cursor.to_list(length=limit)
        
        maintenance_list = []
        for maintenance in maintenance_records:
            maintenance_dict = {k: v for k, v in maintenance.items() if k != "_id"}
            maintenance_dict["id"] = str(maintenance["_id"])
            maintenance_list.append(maintenance_dict)
        
        pages = (total + limit - 1) // limit
        
        logger.info(
            "Maintenance records retrieved successfully",
            user_id=current_user["userId"],
            total=total,
            page=page
        )
        
        return PaginatedResponse(
            data=maintenance_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get maintenance records", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve maintenance records")

@router.post("", response_model=APIResponse)
async def create_maintenance_record(
    maintenance_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Create maintenance record
    
    Input: {"qrCodeId": "qr_code_id", "maintenanceType": "corrective", "workDescription": "Replaced worn rail clip", "partsReplaced": [{"part": "rail_clip", "quantity": 1}], "beforePhotos": ["base64_image_1"], "afterPhotos": ["base64_image_2"]}
    Output: {"success": true, "data": {"maintenanceRecord": {...createdMaintenanceObject}}}
    """
    try:
        if not check_permissions(current_user["role"], "maintenance_records"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        qr_code_id = maintenance_data.get("qrCodeId")
        maintenance_type = maintenance_data.get("maintenanceType", "corrective")
        work_description = maintenance_data.get("workDescription")
        parts_replaced = maintenance_data.get("partsReplaced", [])
        before_photos = maintenance_data.get("beforePhotos", [])
        after_photos = maintenance_data.get("afterPhotos", [])
        
        if not qr_code_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QR code ID is required")
        
        if not work_description:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Work description is required")
        
        # Verify QR code exists
        qr_codes_collection = get_collection("qr_codes")
        qr_code = await qr_codes_collection.find_one({"_id": qr_code_id})
        if not qr_code:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR code not found")
        
        # Process photos
        processed_before_photos = []
        for i, photo in enumerate(before_photos):
            try:
                if photo.startswith('data:image'):
                    photo = photo.split(',')[1]
                
                photo_id = f"before_{qr_code_id}_{i}_{int(datetime.utcnow().timestamp())}"
                processed_before_photos.append({
                    "photoId": photo_id,
                    "data": photo[:100] + "..." if len(photo) > 100 else photo,
                    "uploadedAt": datetime.utcnow()
                })
            except Exception as e:
                logger.warning(f"Failed to process before photo {i}: {str(e)}")
        
        processed_after_photos = []
        for i, photo in enumerate(after_photos):
            try:
                if photo.startswith('data:image'):
                    photo = photo.split(',')[1]
                
                photo_id = f"after_{qr_code_id}_{i}_{int(datetime.utcnow().timestamp())}"
                processed_after_photos.append({
                    "photoId": photo_id,
                    "data": photo[:100] + "..." if len(photo) > 100 else photo,
                    "uploadedAt": datetime.utcnow()
                })
            except Exception as e:
                logger.warning(f"Failed to process after photo {i}: {str(e)}")
        
        # Calculate costs
        total_cost = 0
        for part in parts_replaced:
            part_cost = part.get("unitCost", 0) * part.get("quantity", 1)
            total_cost += part_cost
        
        # Create maintenance record
        maintenance_doc = {
            "qrCodeId": qr_code_id,
            "maintenanceType": maintenance_type,
            "workDescription": work_description,
            "partsReplaced": parts_replaced,
            "beforePhotos": processed_before_photos,
            "afterPhotos": processed_after_photos,
            "totalCost": total_cost,
            "maintenanceDate": datetime.utcnow(),
            "performedBy": current_user["userId"],
            "status": "completed",
            "qualityCheckRequired": maintenance_type in ["corrective", "emergency"],
            "qualityCheckPassed": None,
            "nextMaintenanceDue": datetime.utcnow() + timedelta(days=90),  # Default 90 days
            "remarks": maintenance_data.get("remarks"),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        maintenance_collection = get_collection("maintenance_records")
        result = await maintenance_collection.insert_one(maintenance_doc)
        
        # Get created maintenance record
        created_maintenance = await maintenance_collection.find_one({"_id": result.inserted_id})
        maintenance_dict = {k: v for k, v in created_maintenance.items() if k != "_id"}
        maintenance_dict["id"] = str(created_maintenance["_id"])
        
        logger.info(
            "Maintenance record created successfully",
            user_id=current_user["userId"],
            qr_code_id=qr_code_id,
            maintenance_type=maintenance_type
        )
        
        return APIResponse(
            success=True,
            data={"maintenanceRecord": maintenance_dict}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create maintenance record", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create maintenance record")

@router.put("/{maintenance_id}/quality-check", response_model=APIResponse)
async def quality_check_maintenance(
    maintenance_id: str,
    quality_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Perform quality check on maintenance record
    
    Input: {"qualityCheckPassed": true, "nextMaintenanceDue": "2026-03-15"}
    Output: {"success": true, "data": {"maintenanceRecord": {...updatedMaintenanceObject}}}
    """
    try:
        if not check_permissions(current_user["role"], "maintenance_records"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        quality_check_passed = quality_data.get("qualityCheckPassed")
        next_maintenance_due = quality_data.get("nextMaintenanceDue")
        quality_remarks = quality_data.get("qualityRemarks")
        
        if quality_check_passed is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quality check result is required")
        
        maintenance_collection = get_collection("maintenance_records")
        
        # Check if maintenance record exists
        maintenance = await maintenance_collection.find_one({"_id": maintenance_id})
        if not maintenance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance record not found")
        
        if not maintenance.get("qualityCheckRequired", False):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quality check not required for this maintenance record")
        
        # Update maintenance record
        update_data = {
            "qualityCheckPassed": quality_check_passed,
            "qualityCheckedBy": current_user["userId"],
            "qualityCheckedAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        if next_maintenance_due:
            try:
                next_dt = datetime.fromisoformat(next_maintenance_due.replace("Z", "+00:00"))
                update_data["nextMaintenanceDue"] = next_dt
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid next maintenance due date format")
        
        if quality_remarks:
            update_data["qualityRemarks"] = quality_remarks
        
        await maintenance_collection.update_one(
            {"_id": maintenance_id},
            {"$set": update_data}
        )
        
        # Get updated maintenance record
        updated_maintenance = await maintenance_collection.find_one({"_id": maintenance_id})
        maintenance_dict = {k: v for k, v in updated_maintenance.items() if k != "_id"}
        maintenance_dict["id"] = str(updated_maintenance["_id"])
        
        logger.info(
            "Maintenance quality check completed",
            user_id=current_user["userId"],
            maintenance_id=maintenance_id,
            quality_passed=quality_check_passed
        )
        
        return APIResponse(
            success=True,
            data={"maintenanceRecord": maintenance_dict}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to perform quality check", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to perform quality check")