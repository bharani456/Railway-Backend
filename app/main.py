"""
QR Track Fittings System - Main FastAPI Application
Indian Railways AI-based QR Code Track Fittings Management System
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import structlog
from contextlib import asynccontextmanager

from app.config.database import init_db
from app.config.settings import get_settings
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.routers import (
    auth, users, zones, divisions, stations, vendors, manufacturers,
    fitting_categories, fitting_types, supply_orders, fitting_batches,
    qr_codes, installations, inspections, maintenance_records,
    ai_analysis, reports, analytics, integrations, mobile, notifications,
    search, export, admin, config, batch_operations
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting QR Track Fittings System")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down QR Track Fittings System")

# Create FastAPI application
app = FastAPI(
    title="QR Track Fittings System",
    description="Indian Railways AI-based QR Code Track Fittings Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error("Unhandled exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": "An unexpected error occurred"
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "message": "QR Track Fittings System is running",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["User Management"])
app.include_router(zones.router, prefix="/api/zones", tags=["Zone Management"])
app.include_router(divisions.router, prefix="/api/divisions", tags=["Division Management"])
app.include_router(stations.router, prefix="/api/stations", tags=["Station Management"])
app.include_router(vendors.router, prefix="/api/vendors", tags=["Vendor Management"])
app.include_router(manufacturers.router, prefix="/api/manufacturers", tags=["Manufacturer Management"])
app.include_router(fitting_categories.router, prefix="/api/fitting-categories", tags=["Fitting Categories"])
app.include_router(fitting_types.router, prefix="/api/fitting-types", tags=["Fitting Types"])
app.include_router(supply_orders.router, prefix="/api/supply-orders", tags=["Supply Orders"])
app.include_router(fitting_batches.router, prefix="/api/fitting-batches", tags=["Fitting Batches"])
app.include_router(qr_codes.router, prefix="/api/qr-codes", tags=["QR Codes"])
app.include_router(installations.router, prefix="/api/installations", tags=["Installations"])
app.include_router(inspections.router, prefix="/api/inspections", tags=["Inspections"])
app.include_router(maintenance_records.router, prefix="/api/maintenance-records", tags=["Maintenance Records"])
app.include_router(ai_analysis.router, prefix="/api/ai-analysis", tags=["AI Analysis"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Portal Integrations"])
app.include_router(mobile.router, prefix="/api/mobile", tags=["Mobile App Support"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administration"])
app.include_router(config.router, prefix="/api/config", tags=["Configuration"])
app.include_router(batch_operations.router, prefix="/api/batch", tags=["Batch Operations"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
