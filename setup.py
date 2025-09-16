#!/usr/bin/env python3
"""
Setup script for QR Track Fittings System
"""

import os
import subprocess
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with the provided MongoDB URL"""
    
    env_content = """# QR Track Fittings System - Environment Configuration

# Application
APP_NAME=QR Track Fittings System
APP_VERSION=1.0.0
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# Database - Using your MongoDB URL
MONGODB_URL=mongodb://root:Bharani%4090323@62.72.59.3:27017/?authSource=admin
MONGODB_DATABASE=qr_track_fittings
MONGODB_MAX_CONNECTIONS=100
MONGODB_MIN_CONNECTIONS=10

# Security - CHANGE THESE IN PRODUCTION
SECRET_KEY=qr-track-fittings-secret-key-2025-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
ALLOWED_HOSTS=["localhost", "127.0.0.1", "0.0.0.0"]

# File Upload
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=uploads
ALLOWED_IMAGE_TYPES=["image/jpeg", "image/png", "image/webp"]

# Redis (Optional - for caching and background tasks)
REDIS_URL=redis://localhost:6379

# AI Service
AI_SERVICE_URL=http://localhost:8001
AI_SERVICE_TIMEOUT=30

# External APIs
UDM_PORTAL_URL=https://udm.railways.gov.in/api
TMS_PORTAL_URL=https://tms.railways.gov.in/api

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=200

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Email (Optional)
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=true

# QR Code Settings
QR_CODE_SIZE=10
QR_CODE_BORDER=4
QR_CODE_ERROR_CORRECTION=M

# Image Processing
IMAGE_COMPRESSION_QUALITY=85
THUMBNAIL_SIZE=[300, 300]

# Pagination
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100

# Background Tasks (Optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with your MongoDB configuration")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["uploads", "logs", "temp"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_database_connection():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB connection...")
    
    try:
        from app.config.database import connect_to_mongo
        import asyncio
        
        async def test_connection():
            await connect_to_mongo()
            print("✅ MongoDB connection successful")
        
        asyncio.run(test_connection())
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("Please check your MongoDB URL and ensure the database is accessible")
        return False

def main():
    """Main setup function"""
    print("🚀 QR Track Fittings System Setup")
    print("=" * 50)
    
    # Step 1: Create .env file
    create_env_file()
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return 1
    
    # Step 4: Test database connection
    if not test_database_connection():
        print("❌ Setup failed at database connection test")
        print("Please check your MongoDB URL and try again")
        return 1
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the application: python run.py")
    print("2. Access API docs: http://localhost:8000/docs")
    print("3. Health check: http://localhost:8000/health")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
