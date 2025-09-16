"""
Authentication service for business logic
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import structlog

from app.config.database import get_collection
from app.config.settings import get_settings
from app.utils.security import verify_password, create_access_token, create_refresh_token, get_password_hash
from app.models.user import UserLogin, UserSessionCreate

logger = structlog.get_logger()
settings = get_settings()

class AuthService:
    """Authentication service class"""
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        try:
            users_collection = get_collection("users")
            user = await users_collection.find_one({"email": email})
            
            if not user:
                return None
            
            if not verify_password(password, user.get("passwordHash", "")):
                return None
            
            if not user.get("isActive", False):
                return None
            
            return user
            
        except Exception as e:
            logger.error("Authentication error", error=str(e))
            return None
    
    @staticmethod
    async def create_user_session(user_id: str, device_info: Dict[str, Any], ip_address: str) -> Dict[str, Any]:
        """Create user session"""
        try:
            access_token = create_access_token(data={"sub": user_id})
            refresh_token = create_refresh_token(data={"sub": user_id})
            
            # Calculate expiration times
            access_expires = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            
            # Store session in database
            sessions_collection = get_collection("user_sessions")
            session_data = {
                "userId": user_id,
                "token": access_token,
                "refreshToken": refresh_token,
                "deviceInfo": device_info,
                "ipAddress": ip_address,
                "createdAt": datetime.utcnow(),
                "expiresAt": access_expires,
                "refreshExpiresAt": refresh_expires,
                "isActive": True
            }
            
            await sessions_collection.insert_one(session_data)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": access_expires.isoformat(),
                "refresh_expires_at": refresh_expires.isoformat()
            }
            
        except Exception as e:
            logger.error("Session creation error", error=str(e))
            raise
    
    @staticmethod
    async def revoke_user_session(token: str) -> bool:
        """Revoke user session"""
        try:
            sessions_collection = get_collection("user_sessions")
            result = await sessions_collection.update_one(
                {"token": token},
                {"$set": {"isActive": False, "revokedAt": datetime.utcnow()}}
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error("Session revocation error", error=str(e))
            return False
    
    @staticmethod
    async def refresh_user_token(refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh user access token"""
        try:
            sessions_collection = get_collection("user_sessions")
            session = await sessions_collection.find_one({
                "refreshToken": refresh_token,
                "isActive": True,
                "refreshExpiresAt": {"$gt": datetime.utcnow()}
            })
            
            if not session:
                return None
            
            # Create new access token
            new_access_token = create_access_token(data={"sub": str(session["userId"])})
            new_expires = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
            # Update session
            await sessions_collection.update_one(
                {"_id": session["_id"]},
                {
                    "$set": {
                        "token": new_access_token,
                        "expiresAt": new_expires,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            
            return {
                "access_token": new_access_token,
                "expires_at": new_expires.isoformat()
            }
            
        except Exception as e:
            logger.error("Token refresh error", error=str(e))
            return None
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            users_collection = get_collection("users")
            user = await users_collection.find_one({"_id": user_id})
            return user
            
        except Exception as e:
            logger.error("Get user error", error=str(e))
            return None
    
    @staticmethod
    async def update_last_login(user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            users_collection = get_collection("users")
            result = await users_collection.update_one(
                {"_id": user_id},
                {"$set": {"lastLoginAt": datetime.utcnow()}}
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error("Update last login error", error=str(e))
            return False
