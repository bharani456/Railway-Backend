"""
Export router - Task 16: Export and File Management
APIs: POST /api/export/report, GET /api/export/:exportId/status, GET /api/export/:exportId/download
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import structlog
import uuid

from app.models.base import APIResponse
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.post("/report", response_model=APIResponse)
async def export_report(
    export_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Export report
    
    Input: {"reportType": "inspection_report", "filters": {...}, "format": "pdf", "includePhotos": true}
    Output: {"success": true, "data": {"exportId": "export_12345", "status": "processing", "estimatedTime": "2 minutes"}}
    """
    try:
        if not check_permissions(current_user["role"], "export"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        report_type = export_data.get("reportType")
        filters = export_data.get("filters", {})
        format_type = export_data.get("format", "pdf")
        include_photos = export_data.get("includePhotos", False)
        
        if not report_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Report type is required")
        
        if format_type not in ["pdf", "excel", "csv"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid format. Supported: pdf, excel, csv")
        
        # Generate export ID
        export_id = f"export_{uuid.uuid4().hex[:8]}"
        
        # Create export record
        exports_collection = get_collection("exports")
        export_doc = {
            "exportId": export_id,
            "reportType": report_type,
            "filters": filters,
            "format": format_type,
            "includePhotos": include_photos,
            "status": "processing",
            "requestedBy": current_user["userId"],
            "createdAt": datetime.utcnow(),
            "estimatedCompletion": datetime.utcnow() + timedelta(minutes=2)
        }
        
        await exports_collection.insert_one(export_doc)
        
        # In a real implementation, this would trigger a background job
        # For now, we'll simulate immediate completion
        await exports_collection.update_one(
            {"exportId": export_id},
            {
                "$set": {
                    "status": "completed",
                    "filePath": f"/exports/{export_id}.{format_type}",
                    "fileSize": "2.5 MB",
                    "completedAt": datetime.utcnow(),
                    "expiresAt": datetime.utcnow() + timedelta(days=7)
                }
            }
        )
        
        logger.info(
            "Export report requested",
            user_id=current_user["userId"],
            export_id=export_id,
            report_type=report_type,
            format=format_type
        )
        
        return APIResponse(
            success=True,
            data={
                "exportId": export_id,
                "status": "processing",
                "estimatedTime": "2 minutes"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to export report", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to export report")

@router.get("/{export_id}/status", response_model=APIResponse)
async def get_export_status(
    export_id: str,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Get export status
    
    Input: Export ID in URL
    Output: {"success": true, "data": {"status": "completed", "downloadUrl": "/api/export/export_12345/download", "fileSize": "2.5 MB", "expiresAt": "2025-09-16T10:00:00Z"}}
    """
    try:
        if not check_permissions(current_user["role"], "export"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        exports_collection = get_collection("exports")
        export_doc = await exports_collection.find_one({"exportId": export_id})
        
        if not export_doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
        
        # Check if user owns this export
        if export_doc.get("requestedBy") != current_user["userId"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        status_data = {
            "exportId": export_doc["exportId"],
            "status": export_doc["status"],
            "reportType": export_doc["reportType"],
            "format": export_doc["format"],
            "createdAt": export_doc["createdAt"],
            "fileSize": export_doc.get("fileSize"),
            "expiresAt": export_doc.get("expiresAt")
        }
        
        if export_doc["status"] == "completed":
            status_data["downloadUrl"] = f"/api/export/{export_id}/download"
        
        if export_doc["status"] == "failed":
            status_data["error"] = export_doc.get("error", "Unknown error")
        
        logger.info(
            "Export status retrieved",
            user_id=current_user["userId"],
            export_id=export_id,
            status=export_doc["status"]
        )
        
        return APIResponse(
            success=True,
            data=status_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get export status", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get export status")

@router.get("/{export_id}/download")
async def download_export(
    export_id: str,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Download export file
    
    Input: Export ID in URL
    Output: File download with appropriate headers
    """
    try:
        if not check_permissions(current_user["role"], "export"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        exports_collection = get_collection("exports")
        export_doc = await exports_collection.find_one({"exportId": export_id})
        
        if not export_doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
        
        # Check if user owns this export
        if export_doc.get("requestedBy") != current_user["userId"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        if export_doc["status"] != "completed":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Export not ready for download")
        
        # Check if export has expired
        if export_doc.get("expiresAt") and datetime.utcnow() > export_doc["expiresAt"]:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Export has expired")
        
        # In a real implementation, this would serve the actual file
        # For now, we'll return a mock response
        file_content = f"Mock {export_doc['format'].upper()} export for {export_doc['reportType']}"
        file_name = f"{export_doc['reportType']}_{export_id}.{export_doc['format']}"
        
        logger.info(
            "Export downloaded",
            user_id=current_user["userId"],
            export_id=export_id,
            file_name=file_name
        )
        
        return Response(
            content=file_content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={file_name}",
                "Content-Length": str(len(file_content))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to download export", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to download export")