"""
Authentication router - Task 3: Authentication and Authorization System
APIs: POST /api/auth/login, POST /api/auth/logout, POST /api/auth/refresh
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
import structlog

from app.models.user import UserLogin, UserSessionCreate, UserSessionResponse
from app.models.base import APIResponse
from app.utils.security import verify_password, create_access_token, create_refresh_token, verify_token
from app.config.database import get_collection
from app.config.settings import get_settings

logger = structlog.get_logger()
router = APIRouter()
security = HTTPBearer()
settings = get_settings()

@router.post("/login", response_model=APIResponse)
async def login(login_data: UserLogin, request: Request):
    """
    User login endpoint
    
    Input: {"email": "user@example.com", "password": "password123", "deviceInfo": {...}}
    Output: {"success": true, "data": {"user": {...}, "token": "jwt_token", "expiresAt": "2025-09-16T10:00:00Z"}}
    """
    try:
        # Get user from database
        users_collection = get_collection("users")
        user = await users_collection.find_one({"email": login_data.email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.get("passwordHash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.get("isActive", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # Create tokens
        token_data = {
            "userId": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "zoneId": str(user.get("zoneId", "")),
            "divisionId": str(user.get("divisionId", "")),
            "stationId": str(user.get("stationId", ""))
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Create session
        sessions_collection = get_collection("user_sessions")
        session_data = {
            "userId": user["_id"],
            "token": access_token,
            "refreshToken": refresh_token,
            "deviceInfo": login_data.deviceInfo,
            "ipAddress": request.client.host if request.client else None,
            "userAgent": request.headers.get("user-agent"),
            "isActive": True,
            "expiresAt": expires_at,
            "lastActivity": datetime.utcnow(),
            "createdAt": datetime.utcnow()
        }
        
        await sessions_collection.insert_one(session_data)
        
        # Update user last login
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"lastLoginAt": datetime.utcnow()}}
        )
        
        # Remove password hash from response
        user_response = {k: v for k, v in user.items() if k != "passwordHash"}
        user_response["id"] = str(user["_id"])
        
        logger.info(
            "User logged in successfully",
            user_id=str(user["_id"]),
            email=user["email"],
            role=user["role"]
        )
        
        return APIResponse(
            success=True,
            data={
                "user": user_response,
                "token": access_token,
                "refreshToken": refresh_token,
                "expiresAt": expires_at.isoformat() + "Z"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e), email=login_data.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/logout", response_model=APIResponse)
async def logout(request: Request, current_user: dict = Depends(verify_token)):
    """
    User logout endpoint
    
    Input: Authorization header
    Output: {"success": true, "message": "Logged out successfully"}
    """
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1] if auth_header else None
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization token"
            )
        
        # Deactivate session
        sessions_collection = get_collection("user_sessions")
        await sessions_collection.update_one(
            {
                "userId": current_user["userId"],
                "token": token
            },
            {
                "$set": {
                    "isActive": False,
                    "logoutAt": datetime.utcnow()
                }
            }
        )
        
        logger.info(
            "User logged out successfully",
            user_id=current_user["userId"],
            email=current_user["email"]
        )
        
        return APIResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Logout failed", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/refresh", response_model=APIResponse)
async def refresh_token(refresh_data: dict):
    """
    Refresh access token endpoint
    
    Input: {"refreshToken": "refresh_token_here"}
    Output: {"success": true, "data": {"token": "new_jwt_token", "expiresAt": "2025-09-16T11:00:00Z"}}
    """
    try:
        refresh_token = refresh_data.get("refreshToken")
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )
        
        # Verify refresh token
        try:
            from jose import jwt
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # Check if token is refresh token
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has expired"
                )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if session exists and is active
        sessions_collection = get_collection("user_sessions")
        session = await sessions_collection.find_one({
            "userId": payload["userId"],
            "refreshToken": refresh_token,
            "isActive": True
        })
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )
        
        # Create new access token
        token_data = {
            "userId": payload["userId"],
            "email": payload["email"],
            "role": payload["role"],
            "zoneId": payload.get("zoneId", ""),
            "divisionId": payload.get("divisionId", ""),
            "stationId": payload.get("stationId", "")
        }
        
        new_access_token = create_access_token(token_data)
        expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Update session with new token
        await sessions_collection.update_one(
            {"_id": session["_id"]},
            {
                "$set": {
                    "token": new_access_token,
                    "lastActivity": datetime.utcnow()
                }
            }
        )
        
        logger.info(
            "Token refreshed successfully",
            user_id=payload["userId"],
            email=payload["email"]
        )
        
        return APIResponse(
            success=True,
            data={
                "token": new_access_token,
                "expiresAt": expires_at.isoformat() + "Z"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
