"""
Portal integration router - Task 13: Portal Integration and Sync System
APIs: POST /api/integrations/udm/sync, POST /api/integrations/tms/sync, GET /api/integrations/status
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import structlog
import httpx

from app.models.base import APIResponse, PaginatedResponse, PortalName, RecordType
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection
from app.config.settings import get_settings

logger = structlog.get_logger()
router = APIRouter()
settings = get_settings()

@router.post("/udm/sync", response_model=APIResponse)
async def sync_udm_portal(
    sync_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """Sync with UDM portal"""
    try:
        if not check_permissions(current_user["role"], "integrations"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        record_type = sync_data.get("recordType")
        record_ids = sync_data.get("recordIds", [])
        
        if not record_type or not record_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Record type and IDs are required")
        
        # Mock sync results
        sync_results = []
        for record_id in record_ids:
            sync_results.append({
                "recordId": record_id,
                "status": "synced",
                "udmId": f"UDM_{record_id}",
                "syncedAt": datetime.utcnow().isoformat() + "Z"
            })
        
        # Log sync
        integrations_collection = get_collection("portal_integrations")
        sync_log = {
            "portalName": "UDM",
            "recordType": record_type,
            "recordIds": record_ids,
            "syncResults": sync_results,
            "requestedBy": current_user["userId"],
            "syncDate": datetime.utcnow(),
            "status": "completed"
        }
        await integrations_collection.insert_one(sync_log)
        
        return APIResponse(success=True, data={"syncResults": sync_results})
        
    except Exception as e:
        logger.error("Failed to sync with UDM portal", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to sync with UDM portal")

@router.post("/tms/sync", response_model=APIResponse)
async def sync_tms_portal(
    sync_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """Sync with TMS portal"""
    try:
        if not check_permissions(current_user["role"], "integrations"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        record_type = sync_data.get("recordType")
        record_ids = sync_data.get("recordIds", [])
        
        if not record_type or not record_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Record type and IDs are required")
        
        # Mock sync results
        sync_results = []
        for record_id in record_ids:
            sync_results.append({
                "recordId": record_id,
                "status": "synced",
                "tmsId": f"TMS_{record_id}",
                "syncedAt": datetime.utcnow().isoformat() + "Z"
            })
        
        # Log sync
        integrations_collection = get_collection("portal_integrations")
        sync_log = {
            "portalName": "TMS",
            "recordType": record_type,
            "recordIds": record_ids,
            "syncResults": sync_results,
            "requestedBy": current_user["userId"],
            "syncDate": datetime.utcnow(),
            "status": "completed"
        }
        await integrations_collection.insert_one(sync_log)
        
        return APIResponse(success=True, data={"syncResults": sync_results})
        
    except Exception as e:
        logger.error("Failed to sync with TMS portal", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to sync with TMS portal")

@router.get("/status", response_model=APIResponse)
async def get_integration_status(
    request: Request,
    portalName: Optional[str] = Query(None),
    recordType: Optional[str] = Query(None),
    current_user: dict = Depends(verify_token)
):
    """Get integration status"""
    try:
        if not check_permissions(current_user["role"], "integrations"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Mock integration status
        integration_status = [
            {
                "portalName": "UDM",
                "totalRecords": 1000,
                "syncedRecords": 950,
                "failedRecords": 50,
                "successRate": 95.0,
                "lastSyncAt": datetime.utcnow().isoformat() + "Z"
            },
            {
                "portalName": "TMS",
                "totalRecords": 500,
                "syncedRecords": 480,
                "failedRecords": 20,
                "successRate": 96.0,
                "lastSyncAt": datetime.utcnow().isoformat() + "Z"
            }
        ]
        
        return APIResponse(success=True, data={"integrationStatus": integration_status})
        
    except Exception as e:
        logger.error("Failed to get integration status", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve integration status")
