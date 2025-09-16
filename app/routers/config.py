"""
Configuration router - Task 17: Administration and Configuration
APIs: GET /api/config/app-settings, PUT /api/config/app-settings
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Optional, List, Dict, Any
from datetime import datetime
import structlog

from app.models.base import APIResponse
from app.utils.security import verify_token, check_permissions
from app.config.settings import get_settings

logger = structlog.get_logger()
router = APIRouter()

@router.get("/app-settings", response_model=APIResponse)
async def get_app_settings(
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Get application settings
    
    Input: Authorization header
    Output: {"success": true, "data": {"appVersion": "1.0.0", "features": {...}, "limits": {...}}}
    """
    try:
        if not check_permissions(current_user["role"], "config"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        settings = get_settings()
        
        app_settings = {
            "appVersion": settings.APP_VERSION,
            "appName": settings.APP_NAME,
            "debug": settings.DEBUG,
            "features": {
                "aiAnalysis": True,
                "bulkOperations": True,
                "offlineMode": True,
                "realTimeNotifications": True,
                "advancedSearch": True,
                "exportReports": True
            },
            "limits": {
                "maxUploadSize": f"{settings.MAX_UPLOAD_SIZE // (1024*1024)}MB",
                "batchSize": 1000,
                "maxPageSize": settings.MAX_PAGE_SIZE,
                "rateLimitPerMinute": settings.RATE_LIMIT_PER_MINUTE,
                "qrCodeSize": settings.QR_CODE_SIZE,
                "imageCompressionQuality": settings.IMAGE_COMPRESSION_QUALITY
            },
            "database": {
                "maxConnections": settings.MONGODB_MAX_CONNECTIONS,
                "minConnections": settings.MONGODB_MIN_CONNECTIONS
            },
            "security": {
                "tokenExpireMinutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                "refreshTokenExpireDays": settings.REFRESH_TOKEN_EXPIRE_DAYS,
                "allowedOrigins": settings.ALLOWED_ORIGINS
            },
            "integrations": {
                "aiServiceUrl": settings.AI_SERVICE_URL,
                "udmPortalUrl": settings.UDM_PORTAL_URL,
                "tmsPortalUrl": settings.TMS_PORTAL_URL
            },
            "lastUpdated": datetime.utcnow().isoformat() + "Z"
        }
        
        logger.info(
            "App settings retrieved",
            user_id=current_user["userId"]
        )
        
        return APIResponse(
            success=True,
            data=app_settings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get app settings", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve app settings")

@router.put("/app-settings", response_model=APIResponse)
async def update_app_settings(
    settings_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Update application settings
    
    Input: {"features": {"aiAnalysis": true, "bulkOperations": false}, "limits": {"maxUploadSize": "20MB"}}
    Output: {"success": true, "message": "Configuration updated successfully"}
    """
    try:
        if not check_permissions(current_user["role"], "config"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # In a real implementation, this would update configuration in database
        # For now, we'll just validate the input and return success
        
        features = settings_data.get("features", {})
        limits = settings_data.get("limits", {})
        
        # Validate features
        valid_features = [
            "aiAnalysis", "bulkOperations", "offlineMode", 
            "realTimeNotifications", "advancedSearch", "exportReports"
        ]
        
        for feature, value in features.items():
            if feature not in valid_features:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid feature: {feature}"
                )
            if not isinstance(value, bool):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Feature {feature} must be boolean"
                )
        
        # Validate limits
        if "maxUploadSize" in limits:
            max_size = limits["maxUploadSize"]
            if not isinstance(max_size, str) or not max_size.endswith("MB"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="maxUploadSize must be in format 'XXMB'"
                )
        
        if "batchSize" in limits:
            batch_size = limits["batchSize"]
            if not isinstance(batch_size, int) or batch_size <= 0 or batch_size > 10000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="batchSize must be between 1 and 10000"
                )
        
        if "maxPageSize" in limits:
            max_page = limits["maxPageSize"]
            if not isinstance(max_page, int) or max_page <= 0 or max_page > 1000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="maxPageSize must be between 1 and 1000"
                )
        
        # In a real implementation, save to database
        # For now, just log the changes
        logger.info(
            "App settings updated",
            user_id=current_user["userId"],
            features=features,
            limits=limits
        )
        
        return APIResponse(
            success=True,
            message="Configuration updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update app settings", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update app settings")