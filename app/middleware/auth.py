"""
Authentication middleware
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import structlog

from app.utils.security import verify_token
from app.config.database import get_collection

logger = structlog.get_logger()
security = HTTPBearer()

class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for protected routes"""
    
    # Public routes that don't require authentication
    PUBLIC_ROUTES = {
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/auth/login",
        "/api/auth/refresh"
    }
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public routes
        if request.url.path in self.PUBLIC_ROUTES:
            return await call_next(request)
        
        # Skip authentication for OPTIONS requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Check for authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract token
        token = auth_header.split(" ")[1]
        
        try:
            # Verify token and get user info
            user_data = await verify_token(token)
            
            # Add user info to request state
            request.state.user = user_data
            
            # Check if user session is valid
            sessions_collection = get_collection("user_sessions")
            session = await sessions_collection.find_one({
                "userId": user_data["userId"],
                "token": token,
                "isActive": True
            })
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired session",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Update last activity
            await sessions_collection.update_one(
                {"_id": session["_id"]},
                {"$set": {"lastActivity": user_data["iat"]}}
            )
            
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Authentication error", error=str(exc), path=request.url.path)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return await call_next(request)
