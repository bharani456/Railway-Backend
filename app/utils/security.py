"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import structlog

from app.config.settings import get_settings

logger = structlog.get_logger()
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check if token is expired
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token is refresh token
        if payload.get("type") == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError as e:
        logger.error("JWT verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def check_permissions(user_role: str, required_permission: str) -> bool:
    """Check if user has required permission"""
    # Define role hierarchy and permissions
    role_hierarchy = {
        "super_admin": ["all"],
        "admin": ["users", "zones", "divisions", "stations", "vendors", "manufacturers", 
                "fitting_categories", "fitting_types", "supply_orders", "fitting_batches",
                "qr_codes", "installations", "inspections", "maintenance_records",
                "reports", "analytics", "integrations", "notifications", "search", "export"],
        "manager": ["zones", "divisions", "stations", "fitting_categories", "fitting_types",
                   "supply_orders", "fitting_batches", "qr_codes", "installations",
                   "inspections", "maintenance_records", "reports", "analytics", "notifications"],
        "inspector": ["inspections", "maintenance_records", "qr_codes", "notifications"],
        "operator": ["qr_codes", "installations", "notifications"]
    }
    
    user_permissions = role_hierarchy.get(user_role, [])
    
    if "all" in user_permissions:
        return True
    
    return required_permission in user_permissions

def generate_qr_code_data(fitting_batch_id: str, sequence_number: int) -> str:
    """Generate unique QR code data"""
    import hashlib
    import time
    
    # Create unique identifier
    timestamp = int(time.time())
    data_string = f"{fitting_batch_id}_{sequence_number}_{timestamp}"
    
    # Generate hash for uniqueness
    hash_object = hashlib.md5(data_string.encode())
    hash_hex = hash_object.hexdigest()[:8]
    
    return f"QRTF_{fitting_batch_id}_{sequence_number:06d}_{hash_hex}"

def validate_gps_coordinates(lat: float, lng: float) -> bool:
    """Validate GPS coordinates"""
    return -90 <= lat <= 90 and -180 <= lng <= 180

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone_number(phone: str) -> bool:
    """Validate Indian phone number format"""
    import re
    # Indian phone number pattern (10 digits starting with 6-9)
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def validate_gst_number(gst: str) -> bool:
    """Validate GST number format"""
    import re
    # GST number pattern: 2 digits + 2 letters + 4 digits + 1 letter + 1 digit + 1 letter + 1 digit
    pattern = r'^\d{2}[A-Z]{2}\d{4}[A-Z]{1}\d{1}[A-Z]{1}\d{1}$'
    return re.match(pattern, gst) is not None
