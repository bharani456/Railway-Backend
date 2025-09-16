"""
User management router - Task 4: User and Hierarchy Management APIs
APIs: GET /api/users, POST /api/users, PUT /api/users/:id, DELETE /api/users/:id
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import Optional, List
from datetime import datetime
import structlog

from app.models.user import (
    UserCreate, UserUpdate, UserResponse, UserListParams, 
    UserStats, UserProfile, UserRole
)
from app.models.base import APIResponse, PaginatedResponse
from app.utils.security import verify_token, get_password_hash, check_permissions
from app.config.database import get_collection

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_users(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    zoneId: Optional[str] = Query(None, description="Filter by zone ID"),
    divisionId: Optional[str] = Query(None, description="Filter by division ID"),
    stationId: Optional[str] = Query(None, description="Filter by station ID"),
    sortBy: Optional[str] = Query("createdAt", description="Sort field"),
    sortOrder: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: dict = Depends(verify_token)
):
    """
    Get users with pagination and filters
    
    Input: Query params (page=1, limit=10, role="inspector", status="active", search="john")
    Output: {"success": true, "data": {"users": [...], "pagination": {"page": 1, "limit": 10, "total": 100, "pages": 10}}}
    """
    try:
        # Check permissions
        if not check_permissions(current_user["role"], "users"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Build query
        query = {}
        
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"employeeId": {"$regex": search, "$options": "i"}}
            ]
        
        if role:
            query["role"] = role.value
        
        if status:
            query["status"] = status
        
        if zoneId:
            query["zoneId"] = zoneId
        
        if divisionId:
            query["divisionId"] = divisionId
        
        if stationId:
            query["stationId"] = stationId
        
        # Get users collection
        users_collection = get_collection("users")
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Build sort
        sort_direction = 1 if sortOrder == "asc" else -1
        sort_field = sortBy if sortBy in ["name", "email", "role", "createdAt", "updatedAt"] else "createdAt"
        
        # Get total count
        total = await users_collection.count_documents(query)
        
        # Get users
        cursor = users_collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        
        # Remove password hash and format response
        user_list = []
        for user in users:
            user_dict = {k: v for k, v in user.items() if k != "passwordHash"}
            user_dict["id"] = str(user["_id"])
            user_list.append(user_dict)
        
        # Calculate pagination info
        pages = (total + limit - 1) // limit
        
        logger.info(
            "Users retrieved successfully",
            user_id=current_user["userId"],
            total=total,
            page=page,
            limit=limit
        )
        
        return PaginatedResponse(
            data=user_list,
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
        logger.error("Failed to get users", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.post("", response_model=APIResponse)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Create a new user
    
    Input: {"name": "John Doe", "email": "john@example.com", "role": "inspector", "zoneId": "zone_id"}
    Output: {"success": true, "data": {"user": {...createdUserObject}}}
    """
    try:
        # Check permissions
        if not check_permissions(current_user["role"], "users"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Get users collection
        users_collection = get_collection("users")
        
        # Check if email already exists
        existing_user = await users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Check if employee ID already exists
        if user_data.employeeId:
            existing_employee = await users_collection.find_one({"employeeId": user_data.employeeId})
            if existing_employee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee ID already exists"
                )
        
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Create user document
        user_doc = {
            "name": user_data.name,
            "email": user_data.email,
            "employeeId": user_data.employeeId,
            "phone": user_data.phone,
            "role": user_data.role.value,
            "zoneId": user_data.zoneId,
            "divisionId": user_data.divisionId,
            "stationId": user_data.stationId,
            "isActive": user_data.isActive,
            "profilePicture": user_data.profilePicture,
            "passwordHash": password_hash,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": current_user["userId"],
            "status": "active"
        }
        
        # Insert user
        result = await users_collection.insert_one(user_doc)
        
        # Get created user
        created_user = await users_collection.find_one({"_id": result.inserted_id})
        created_user_dict = {k: v for k, v in created_user.items() if k != "passwordHash"}
        created_user_dict["id"] = str(created_user["_id"])
        
        logger.info(
            "User created successfully",
            user_id=current_user["userId"],
            created_user_id=str(result.inserted_id),
            email=user_data.email
        )
        
        return APIResponse(
            success=True,
            data={"user": created_user_dict}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create user", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.put("/{user_id}", response_model=APIResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Update a user
    
    Input: {"name": "Updated Name", "status": "active"}
    Output: {"success": true, "data": {"user": {...updatedUserObject}}}
    """
    try:
        # Check permissions
        if not check_permissions(current_user["role"], "users"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Get users collection
        users_collection = get_collection("users")
        
        # Check if user exists
        existing_user = await users_collection.find_one({"_id": user_id})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if email already exists (if being updated)
        if user_data.email and user_data.email != existing_user["email"]:
            email_exists = await users_collection.find_one({
                "email": user_data.email,
                "_id": {"$ne": user_id}
            })
            if email_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Check if employee ID already exists (if being updated)
        if user_data.employeeId and user_data.employeeId != existing_user.get("employeeId"):
            employee_exists = await users_collection.find_one({
                "employeeId": user_data.employeeId,
                "_id": {"$ne": user_id}
            })
            if employee_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee ID already exists"
                )
        
        # Build update data
        update_data = {k: v for k, v in user_data.dict(exclude_unset=True).items() if v is not None}
        update_data["updatedAt"] = datetime.utcnow()
        update_data["updatedBy"] = current_user["userId"]
        
        # Update user
        await users_collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        # Get updated user
        updated_user = await users_collection.find_one({"_id": user_id})
        updated_user_dict = {k: v for k, v in updated_user.items() if k != "passwordHash"}
        updated_user_dict["id"] = str(updated_user["_id"])
        
        logger.info(
            "User updated successfully",
            user_id=current_user["userId"],
            updated_user_id=user_id
        )
        
        return APIResponse(
            success=True,
            data={"user": updated_user_dict}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update user", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(
    user_id: str,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Delete a user (soft delete)
    
    Input: User ID in URL
    Output: {"success": true, "message": "User deleted successfully"}
    """
    try:
        # Check permissions
        if not check_permissions(current_user["role"], "users"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Prevent self-deletion
        if user_id == current_user["userId"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Get users collection
        users_collection = get_collection("users")
        
        # Check if user exists
        existing_user = await users_collection.find_one({"_id": user_id})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Soft delete user
        await users_collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "status": "deleted",
                    "isActive": False,
                    "deletedAt": datetime.utcnow(),
                    "deletedBy": current_user["userId"],
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        logger.info(
            "User deleted successfully",
            user_id=current_user["userId"],
            deleted_user_id=user_id
        )
        
        return APIResponse(
            success=True,
            message="User deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete user", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.get("/stats", response_model=APIResponse)
async def get_user_stats(
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Get user statistics
    """
    try:
        # Check permissions
        if not check_permissions(current_user["role"], "users"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        users_collection = get_collection("users")
        
        # Get statistics
        total_users = await users_collection.count_documents({"status": {"$ne": "deleted"}})
        active_users = await users_collection.count_documents({"isActive": True, "status": {"$ne": "deleted"}})
        inactive_users = await users_collection.count_documents({"isActive": False, "status": {"$ne": "deleted"}})
        
        # Get users by role
        role_pipeline = [
            {"$match": {"status": {"$ne": "deleted"}}},
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]
        role_cursor = users_collection.aggregate(role_pipeline)
        users_by_role = {doc["_id"]: doc["count"] for doc in await role_cursor.to_list(length=None)}
        
        # Get users by zone
        zone_pipeline = [
            {"$match": {"status": {"$ne": "deleted"}, "zoneId": {"$ne": None}}},
            {"$group": {"_id": "$zoneId", "count": {"$sum": 1}}}
        ]
        zone_cursor = users_collection.aggregate(zone_pipeline)
        users_by_zone = {str(doc["_id"]): doc["count"] for doc in await zone_cursor.to_list(length=None)}
        
        # Get recent logins (last 24 hours)
        recent_logins = await users_collection.count_documents({
            "lastLoginAt": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)},
            "status": {"$ne": "deleted"}
        })
        
        stats = UserStats(
            totalUsers=total_users,
            activeUsers=active_users,
            inactiveUsers=inactive_users,
            usersByRole=users_by_role,
            usersByZone=users_by_zone,
            recentLogins=recent_logins
        )
        
        logger.info(
            "User stats retrieved successfully",
            user_id=current_user["userId"]
        )
        
        return APIResponse(
            success=True,
            data=stats.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user stats", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )
