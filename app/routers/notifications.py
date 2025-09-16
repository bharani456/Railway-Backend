"""
Notifications router - Task 15: Notification and Search Systems
APIs: GET /api/notifications, PUT /api/notifications/:id/read, POST /api/notifications/bulk-read
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import structlog

from app.models.base import APIResponse, PaginatedResponse, NotificationType
from app.utils.security import verify_token, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_notifications(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    userId: Optional[str] = Query(None),
    unreadOnly: bool = Query(False),
    type: Optional[str] = Query(None),
    current_user: dict = Depends(verify_token)
):
    """
    Get notifications
    
    Input: Query params (userId="user_id", unreadOnly=true, type="inspection_due")
    Output: {"success": true, "data": {"notifications": [...], "unreadCount": 3}}
    """
    try:
        if not check_permissions(current_user["role"], "notifications"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Build query
        query = {}
        if userId:
            query["userId"] = userId
        else:
            query["userId"] = current_user["userId"]
        
        if unreadOnly:
            query["isRead"] = False
        
        if type:
            query["type"] = type
        
        notifications_collection = get_collection("notifications")
        skip = (page - 1) * limit
        
        total = await notifications_collection.count_documents(query)
        cursor = notifications_collection.find(query).sort("createdAt", -1).skip(skip).limit(limit)
        notifications = await cursor.to_list(length=limit)
        
        notification_list = []
        for notification in notifications:
            notification_dict = {k: v for k, v in notification.items() if k != "_id"}
            notification_dict["id"] = str(notification["_id"])
            notification_list.append(notification_dict)
        
        # Get unread count
        unread_query = {"userId": current_user["userId"], "isRead": False}
        unread_count = await notifications_collection.count_documents(unread_query)
        
        pages = (total + limit - 1) // limit
        
        logger.info(
            "Notifications retrieved successfully",
            user_id=current_user["userId"],
            total=total,
            unread_count=unread_count
        )
        
        return PaginatedResponse(
            data=notification_list,
            pagination={
                "page": page, "limit": limit, "total": total, "pages": pages,
                "hasNext": page < pages, "hasPrev": page > 1, "unreadCount": unread_count
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get notifications", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve notifications")

@router.put("/{notification_id}/read", response_model=APIResponse)
async def mark_notification_read(
    notification_id: str,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Mark a notification as read
    
    Input: Notification ID in URL
    Output: {"success": true, "message": "Notification marked as read"}
    """
    try:
        if not check_permissions(current_user["role"], "notifications"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        notifications_collection = get_collection("notifications")
        
        # Check if notification exists and belongs to user
        notification = await notifications_collection.find_one({
            "_id": notification_id,
            "userId": current_user["userId"]
        })
        
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        
        # Mark as read
        await notifications_collection.update_one(
            {"_id": notification_id},
            {
                "$set": {
                    "isRead": True,
                    "readAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        logger.info(
            "Notification marked as read",
            user_id=current_user["userId"],
            notification_id=notification_id
        )
        
        return APIResponse(
            success=True,
            message="Notification marked as read"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to mark notification as read", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to mark notification as read")

@router.post("/bulk-read", response_model=APIResponse)
async def mark_notifications_bulk_read(
    bulk_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Mark multiple notifications as read
    
    Input: {"notificationIds": ["id1", "id2", "id3"]}
    Output: {"success": true, "message": "Notifications marked as read", "count": 3}
    """
    try:
        if not check_permissions(current_user["role"], "notifications"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        notification_ids = bulk_data.get("notificationIds", [])
        
        if not notification_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Notification IDs are required")
        
        notifications_collection = get_collection("notifications")
        
        # Mark notifications as read
        result = await notifications_collection.update_many(
            {
                "_id": {"$in": notification_ids},
                "userId": current_user["userId"]
            },
            {
                "$set": {
                    "isRead": True,
                    "readAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        logger.info(
            "Notifications marked as read in bulk",
            user_id=current_user["userId"],
            count=result.modified_count
        )
        
        return APIResponse(
            success=True,
            message="Notifications marked as read",
            data={"count": result.modified_count}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to mark notifications as read in bulk", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to mark notifications as read")