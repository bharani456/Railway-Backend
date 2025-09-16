"""
Inspection management router - Task 10: Inspection Management System
APIs: GET /api/inspections, POST /api/inspections, PUT /api/inspections/:id/complete, GET /api/inspections/:id/photos/:photoIndex
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request, Response
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import structlog
import base64

from app.models.base import APIResponse, PaginatedResponse, InspectionType, InspectionStatus
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_inspections(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    qrCodeId: Optional[str] = Query(None),
    inspectorId: Optional[str] = Query(None),
    inspectionType: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    dateRange: Optional[str] = Query(None),
    current_user: dict = Depends(verify_token)
):
    """
    Get inspections with filters
    
    Input: Query params (qrCodeId="qr_id", inspectorId="inspector_id", inspectionType="routine", dateRange="2025-01-01,2025-12-31")
    Output: {"success": true, "data": {"inspections": [...], "pagination": {...}}}
    """
    try:
        if not check_permissions(current_user["role"], "inspections"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Build query
        query = {}
        
        if qrCodeId:
            query["qrCodeId"] = qrCodeId
        if inspectorId:
            query["inspectorId"] = inspectorId
        if inspectionType:
            query["inspectionType"] = inspectionType
        if status:
            query["status"] = status
        
        if dateRange:
            try:
                start_date, end_date = dateRange.split(",")
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                query["inspectionDate"] = {"$gte": start_dt, "$lte": end_dt}
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date range format")
        
        inspections_collection = get_collection("inspections")
        skip = (page - 1) * limit
        
        total = await inspections_collection.count_documents(query)
        cursor = inspections_collection.find(query).sort("inspectionDate", -1).skip(skip).limit(limit)
        inspections = await cursor.to_list(length=limit)
        
        inspection_list = []
        for inspection in inspections:
            inspection_dict = {k: v for k, v in inspection.items() if k != "_id"}
            inspection_dict["id"] = str(inspection["_id"])
            inspection_list.append(inspection_dict)
        
        pages = (total + limit - 1) // limit
        
        logger.info(
            "Inspections retrieved successfully",
            user_id=current_user["userId"],
            total=total,
            page=page
        )
        
        return PaginatedResponse(
            data=inspection_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get inspections", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve inspections")

@router.post("", response_model=APIResponse)
async def create_inspection(
    inspection_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Create inspection record
    
    Input: {"qrCodeId": "qr_code_id", "inspectionType": "routine", "checklistData": {...}, "visualCondition": "good", "photos": ["base64_image_1", "base64_image_2"]}
    Output: {"success": true, "data": {"inspection": {...createdInspectionObject}}}
    """
    try:
        if not check_permissions(current_user["role"], "inspections"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        qr_code_id = inspection_data.get("qrCodeId")
        inspection_type = inspection_data.get("inspectionType", "routine")
        checklist_data = inspection_data.get("checklistData", {})
        visual_condition = inspection_data.get("visualCondition")
        photos = inspection_data.get("photos", [])
        
        if not qr_code_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QR code ID is required")
        
        # Verify QR code exists
        qr_codes_collection = get_collection("qr_codes")
        qr_code = await qr_codes_collection.find_one({"_id": qr_code_id})
        if not qr_code:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR code not found")
        
        # Process photos
        processed_photos = []
        for i, photo in enumerate(photos):
            try:
                # Decode base64 image
                if photo.startswith('data:image'):
                    photo = photo.split(',')[1]
                
                # Store photo (in real implementation, would save to file system or cloud storage)
                photo_id = f"photo_{qr_code_id}_{i}_{int(datetime.utcnow().timestamp())}"
                processed_photos.append({
                    "photoId": photo_id,
                    "data": photo[:100] + "..." if len(photo) > 100 else photo,  # Truncate for storage
                    "uploadedAt": datetime.utcnow()
                })
            except Exception as e:
                logger.warning(f"Failed to process photo {i}: {str(e)}")
        
        # Create inspection record
        inspection_doc = {
            "qrCodeId": qr_code_id,
            "inspectionType": inspection_type,
            "inspectorId": current_user["userId"],
            "inspectionDate": datetime.utcnow(),
            "checklistData": checklist_data,
            "visualCondition": visual_condition,
            "photos": processed_photos,
            "status": "in_progress",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        inspections_collection = get_collection("inspections")
        result = await inspections_collection.insert_one(inspection_doc)
        
        # Get created inspection
        created_inspection = await inspections_collection.find_one({"_id": result.inserted_id})
        inspection_dict = {k: v for k, v in created_inspection.items() if k != "_id"}
        inspection_dict["id"] = str(created_inspection["_id"])
        
        logger.info(
            "Inspection created successfully",
            user_id=current_user["userId"],
            qr_code_id=qr_code_id,
            inspection_type=inspection_type
        )
        
        return APIResponse(
            success=True,
            data={"inspection": inspection_dict}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create inspection", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create inspection")

@router.put("/{inspection_id}/complete", response_model=APIResponse)
async def complete_inspection(
    inspection_id: str,
    completion_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Complete inspection
    
    Input: {"recommendation": "pass", "nextInspectionDue": "2025-12-15", "remarks": "All parameters within limits"}
    Output: {"success": true, "data": {"inspection": {...completedInspectionObject}}}
    """
    try:
        if not check_permissions(current_user["role"], "inspections"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        recommendation = completion_data.get("recommendation")
        next_inspection_due = completion_data.get("nextInspectionDue")
        remarks = completion_data.get("remarks")
        
        if not recommendation:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recommendation is required")
        
        valid_recommendations = ["pass", "fail", "conditional_pass", "needs_attention"]
        if recommendation not in valid_recommendations:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid recommendation. Valid options: {valid_recommendations}")
        
        inspections_collection = get_collection("inspections")
        
        # Check if inspection exists
        inspection = await inspections_collection.find_one({"_id": inspection_id})
        if not inspection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
        
        if inspection["status"] != "in_progress":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inspection is not in progress")
        
        # Update inspection
        update_data = {
            "status": "completed",
            "recommendation": recommendation,
            "remarks": remarks,
            "completedAt": datetime.utcnow(),
            "completedBy": current_user["userId"],
            "updatedAt": datetime.utcnow()
        }
        
        if next_inspection_due:
            try:
                next_dt = datetime.fromisoformat(next_inspection_due.replace("Z", "+00:00"))
                update_data["nextInspectionDue"] = next_dt
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid next inspection due date format")
        
        await inspections_collection.update_one(
            {"_id": inspection_id},
            {"$set": update_data}
        )
        
        # Get updated inspection
        updated_inspection = await inspections_collection.find_one({"_id": inspection_id})
        inspection_dict = {k: v for k, v in updated_inspection.items() if k != "_id"}
        inspection_dict["id"] = str(updated_inspection["_id"])
        
        logger.info(
            "Inspection completed successfully",
            user_id=current_user["userId"],
            inspection_id=inspection_id,
            recommendation=recommendation
        )
        
        return APIResponse(
            success=True,
            data={"inspection": inspection_dict}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to complete inspection", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to complete inspection")

@router.get("/{inspection_id}/photos/{photo_index}")
async def get_inspection_photo(
    inspection_id: str,
    photo_index: int,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Get inspection photo
    
    Input: Inspection ID and photo index in URL
    Output: Binary image data with appropriate content-type header
    """
    try:
        if not check_permissions(current_user["role"], "inspections"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        inspections_collection = get_collection("inspections")
        inspection = await inspections_collection.find_one({"_id": inspection_id})
        
        if not inspection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
        
        photos = inspection.get("photos", [])
        if photo_index >= len(photos):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
        
        photo_data = photos[photo_index]
        photo_content = photo_data.get("data", "")
        
        # In a real implementation, this would return the actual image file
        # For now, we'll return a placeholder
        placeholder_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        logger.info(
            "Inspection photo retrieved",
            user_id=current_user["userId"],
            inspection_id=inspection_id,
            photo_index=photo_index
        )
        
        return Response(
            content=base64.b64decode(placeholder_image),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=photo_{photo_index}.png"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get inspection photo", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve inspection photo")