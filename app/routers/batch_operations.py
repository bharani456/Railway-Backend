"""
Batch operations router - Task 18: Batch Operations and Final APIs
APIs: POST /api/batch/bulk-inspection, POST /api/batch/bulk-maintenance
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import structlog
import uuid

from app.models.base import APIResponse
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.post("/bulk-inspection", response_model=APIResponse)
async def bulk_inspection(
    inspection_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Schedule bulk inspections
    
    Input: {"qrCodeIds": ["qr1", "qr2", "qr3"], "inspectionType": "routine", "scheduledDate": "2025-09-20", "assignedInspector": "inspector_id"}
    Output: {"success": true, "data": {"scheduledInspections": 3, "batchId": "batch_inspection_123"}}
    """
    try:
        if not check_permissions(current_user["role"], "batch_operations"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        qr_code_ids = inspection_data.get("qrCodeIds", [])
        inspection_type = inspection_data.get("inspectionType", "routine")
        scheduled_date = inspection_data.get("scheduledDate")
        assigned_inspector = inspection_data.get("assignedInspector")
        
        if not qr_code_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QR code IDs are required")
        
        if not inspection_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inspection type is required")
        
        if not scheduled_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scheduled date is required")
        
        # Parse scheduled date
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid scheduled date format")
        
        # Generate batch ID
        batch_id = f"batch_inspection_{uuid.uuid4().hex[:8]}"
        
        # Create inspection records
        inspections_collection = get_collection("inspections")
        created_inspections = []
        
        for qr_code_id in qr_code_ids:
            inspection_doc = {
                "qrCodeId": qr_code_id,
                "inspectionType": inspection_type,
                "status": "scheduled",
                "scheduledDate": scheduled_dt,
                "assignedInspector": assigned_inspector,
                "batchId": batch_id,
                "createdBy": current_user["userId"],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            result = await inspections_collection.insert_one(inspection_doc)
            created_inspections.append(str(result.inserted_id))
        
        # Create batch record
        batches_collection = get_collection("batch_operations")
        batch_doc = {
            "batchId": batch_id,
            "operationType": "bulk_inspection",
            "qrCodeIds": qr_code_ids,
            "inspectionType": inspection_type,
            "scheduledDate": scheduled_dt,
            "assignedInspector": assigned_inspector,
            "status": "scheduled",
            "totalItems": len(qr_code_ids),
            "completedItems": 0,
            "createdBy": current_user["userId"],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        await batches_collection.insert_one(batch_doc)
        
        logger.info(
            "Bulk inspection scheduled",
            user_id=current_user["userId"],
            batch_id=batch_id,
            total_inspections=len(qr_code_ids),
            inspection_type=inspection_type
        )
        
        return APIResponse(
            success=True,
            data={
                "scheduledInspections": len(qr_code_ids),
                "batchId": batch_id,
                "scheduledDate": scheduled_dt.isoformat() + "Z"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to schedule bulk inspection", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to schedule bulk inspection")

@router.post("/bulk-maintenance", response_model=APIResponse)
async def bulk_maintenance(
    maintenance_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Schedule bulk maintenance
    
    Input: {"filters": {"zoneId": "zone_id", "status": "maintenance_due"}, "maintenanceType": "preventive", "scheduledDate": "2025-09-25"}
    Output: {"success": true, "data": {"affectedFittings": 150, "scheduledMaintenance": 150, "batchId": "batch_maintenance_456"}}
    """
    try:
        if not check_permissions(current_user["role"], "batch_operations"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        filters = maintenance_data.get("filters", {})
        maintenance_type = maintenance_data.get("maintenanceType", "preventive")
        scheduled_date = maintenance_data.get("scheduledDate")
        
        if not maintenance_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maintenance type is required")
        
        if not scheduled_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scheduled date is required")
        
        # Parse scheduled date
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid scheduled date format")
        
        # Build query for QR codes based on filters
        qr_query = {}
        
        if filters.get("zoneId"):
            installations_collection = get_collection("fitting_installations")
            installations = await installations_collection.find(
                {"zoneId": filters["zoneId"]},
                {"qrCodeId": 1}
            ).to_list(length=None)
            qr_code_ids = [inst["qrCodeId"] for inst in installations]
            qr_query["_id"] = {"$in": qr_code_ids}
        
        if filters.get("status"):
            qr_query["status"] = filters["status"]
        
        if filters.get("divisionId"):
            installations_collection = get_collection("fitting_installations")
            installations = await installations_collection.find(
                {"divisionId": filters["divisionId"]},
                {"qrCodeId": 1}
            ).to_list(length=None)
            qr_code_ids = [inst["qrCodeId"] for inst in installations]
            if qr_query.get("_id"):
                qr_query["_id"]["$in"] = list(set(qr_query["_id"]["$in"]) & set(qr_code_ids))
            else:
                qr_query["_id"] = {"$in": qr_code_ids}
        
        if filters.get("stationId"):
            installations_collection = get_collection("fitting_installations")
            installations = await installations_collection.find(
                {"stationId": filters["stationId"]},
                {"qrCodeId": 1}
            ).to_list(length=None)
            qr_code_ids = [inst["qrCodeId"] for inst in installations]
            if qr_query.get("_id"):
                qr_query["_id"]["$in"] = list(set(qr_query["_id"]["$in"]) & set(qr_code_ids))
            else:
                qr_query["_id"] = {"$in": qr_code_ids}
        
        # Get QR codes to schedule maintenance for
        qr_codes_collection = get_collection("qr_codes")
        qr_codes = await qr_codes_collection.find(qr_query).to_list(length=None)
        
        if not qr_codes:
            return APIResponse(
                success=True,
                data={
                    "affectedFittings": 0,
                    "scheduledMaintenance": 0,
                    "batchId": None
                }
            )
        
        # Generate batch ID
        batch_id = f"batch_maintenance_{uuid.uuid4().hex[:8]}"
        
        # Create maintenance records
        maintenance_collection = get_collection("maintenance_records")
        created_maintenance = []
        
        for qr_code in qr_codes:
            maintenance_doc = {
                "qrCodeId": str(qr_code["_id"]),
                "maintenanceType": maintenance_type,
                "status": "scheduled",
                "scheduledDate": scheduled_dt,
                "batchId": batch_id,
                "createdBy": current_user["userId"],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            result = await maintenance_collection.insert_one(maintenance_doc)
            created_maintenance.append(str(result.inserted_id))
        
        # Create batch record
        batches_collection = get_collection("batch_operations")
        batch_doc = {
            "batchId": batch_id,
            "operationType": "bulk_maintenance",
            "filters": filters,
            "maintenanceType": maintenance_type,
            "scheduledDate": scheduled_dt,
            "status": "scheduled",
            "totalItems": len(qr_codes),
            "completedItems": 0,
            "createdBy": current_user["userId"],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        await batches_collection.insert_one(batch_doc)
        
        logger.info(
            "Bulk maintenance scheduled",
            user_id=current_user["userId"],
            batch_id=batch_id,
            total_maintenance=len(qr_codes),
            maintenance_type=maintenance_type
        )
        
        return APIResponse(
            success=True,
            data={
                "affectedFittings": len(qr_codes),
                "scheduledMaintenance": len(qr_codes),
                "batchId": batch_id,
                "scheduledDate": scheduled_dt.isoformat() + "Z"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to schedule bulk maintenance", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to schedule bulk maintenance")