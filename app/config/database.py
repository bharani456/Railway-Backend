"""
MongoDB database configuration and connection management
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from typing import Optional
import asyncio
import structlog

from app.config.settings import get_settings, get_database_url

logger = structlog.get_logger()

class Database:
    """Database connection manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

# Global database instance
db = Database()

async def connect_to_mongo():
    """Create database connection"""
    settings = get_settings()
    try:
        db.client = AsyncIOMotorClient(
            get_database_url(),
            maxPoolSize=settings.MONGODB_MAX_CONNECTIONS,
            minPoolSize=settings.MONGODB_MIN_CONNECTIONS,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000
        )
        db.database = db.client[settings.MONGODB_DATABASE]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
    except Exception as e:
        logger.error("Failed to connect to MongoDB", error=str(e))
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if db.database is None:
        raise RuntimeError("Database not initialized")
    return db.database

async def init_db():
    """Initialize database with collections and indexes"""
    await connect_to_mongo()
    await create_indexes()

async def create_indexes():
    """Create database indexes for optimal performance"""
    database = get_database()
    
    # Users collection indexes
    await database.users.create_indexes([
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("employeeId", ASCENDING)], unique=True, sparse=True),
        IndexModel([("role", ASCENDING)]),
        IndexModel([("zoneId", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("createdAt", DESCENDING)]),
        IndexModel([("name", TEXT), ("email", TEXT)], name="user_search")
    ])
    
    # Zones collection indexes
    await database.zones.create_indexes([
        IndexModel([("code", ASCENDING)], unique=True),
        IndexModel([("name", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("name", TEXT)], name="zone_search")
    ])
    
    # Divisions collection indexes
    await database.divisions.create_indexes([
        IndexModel([("code", ASCENDING)], unique=True),
        IndexModel([("zoneId", ASCENDING)]),
        IndexModel([("name", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("name", TEXT)], name="division_search")
    ])
    
    # Stations collection indexes
    await database.stations.create_indexes([
        IndexModel([("code", ASCENDING)], unique=True),
        IndexModel([("divisionId", ASCENDING)]),
        IndexModel([("name", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("coordinates.lat", ASCENDING), ("coordinates.lng", ASCENDING)]),
        IndexModel([("name", TEXT)], name="station_search")
    ])
    
    # Vendors collection indexes
    await database.vendors.create_indexes([
        IndexModel([("gstNumber", ASCENDING)], unique=True, sparse=True),
        IndexModel([("name", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("name", TEXT)], name="vendor_search")
    ])
    
    # Manufacturers collection indexes
    await database.manufacturers.create_indexes([
        IndexModel([("code", ASCENDING)], unique=True),
        IndexModel([("name", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("name", TEXT)], name="manufacturer_search")
    ])
    
    # Fitting categories collection indexes
    await database.fitting_categories.create_indexes([
        IndexModel([("code", ASCENDING)], unique=True),
        IndexModel([("name", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("name", TEXT)], name="category_search")
    ])
    
    # Fitting types collection indexes
    await database.fitting_types.create_indexes([
        IndexModel([("categoryId", ASCENDING)]),
        IndexModel([("model", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("name", TEXT), ("model", TEXT)], name="fitting_type_search")
    ])
    
    # Supply orders collection indexes
    await database.supply_orders.create_indexes([
        IndexModel([("orderNumber", ASCENDING)], unique=True),
        IndexModel([("vendorId", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("orderDate", DESCENDING)]),
        IndexModel([("expectedDeliveryDate", ASCENDING)]),
        IndexModel([("orderNumber", TEXT)], name="order_search")
    ])
    
    # Fitting batches collection indexes
    await database.fitting_batches.create_indexes([
        IndexModel([("batchNumber", ASCENDING)], unique=True),
        IndexModel([("supplyOrderId", ASCENDING)]),
        IndexModel([("manufacturerId", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("manufacturingDate", DESCENDING)]),
        IndexModel([("batchNumber", TEXT)], name="batch_search")
    ])
    
    # QR codes collection indexes
    await database.qr_codes.create_indexes([
        IndexModel([("qrCode", ASCENDING)], unique=True),
        IndexModel([("fittingBatchId", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("generatedAt", DESCENDING)]),
        IndexModel([("qrCode", TEXT)], name="qr_search")
    ])
    
    # Fitting installations collection indexes
    await database.fitting_installations.create_indexes([
        IndexModel([("qrCodeId", ASCENDING)], unique=True),
        IndexModel([("zoneId", ASCENDING)]),
        IndexModel([("divisionId", ASCENDING)]),
        IndexModel([("stationId", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("installationDate", DESCENDING)]),
        IndexModel([("trackSection", ASCENDING)]),
        IndexModel([("coordinates.lat", ASCENDING), ("coordinates.lng", ASCENDING)]),
        IndexModel([("trackSection", TEXT)], name="installation_search")
    ])
    
    # Inspections collection indexes
    await database.inspections.create_indexes([
        IndexModel([("qrCodeId", ASCENDING)]),
        IndexModel([("inspectorId", ASCENDING)]),
        IndexModel([("inspectionType", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("inspectionDate", DESCENDING)]),
        IndexModel([("nextInspectionDue", ASCENDING)])
    ])
    
    # Maintenance records collection indexes
    await database.maintenance_records.create_indexes([
        IndexModel([("qrCodeId", ASCENDING)]),
        IndexModel([("performedBy", ASCENDING)]),
        IndexModel([("maintenanceType", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("maintenanceDate", DESCENDING)]),
        IndexModel([("nextMaintenanceDue", ASCENDING)])
    ])
    
    # QR scan logs collection indexes
    await database.qr_scan_logs.create_indexes([
        IndexModel([("qrCodeId", ASCENDING)]),
        IndexModel([("scannedBy", ASCENDING)]),
        IndexModel([("scanPurpose", ASCENDING)]),
        IndexModel([("scanDate", DESCENDING)]),
        IndexModel([("coordinates.lat", ASCENDING), ("coordinates.lng", ASCENDING)])
    ])
    
    # AI analysis reports collection indexes
    await database.ai_analysis_reports.create_indexes([
        IndexModel([("qrCodeId", ASCENDING)]),
        IndexModel([("analysisType", ASCENDING)]),
        IndexModel([("riskLevel", ASCENDING)]),
        IndexModel([("createdAt", DESCENDING)]),
        IndexModel([("status", ASCENDING)])
    ])
    
    # Portal integrations collection indexes
    await database.portal_integrations.create_indexes([
        IndexModel([("portalName", ASCENDING)]),
        IndexModel([("recordType", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("syncDate", DESCENDING)]),
        IndexModel([("recordId", ASCENDING)])
    ])
    
    # User sessions collection indexes
    await database.user_sessions.create_indexes([
        IndexModel([("userId", ASCENDING)]),
        IndexModel([("token", ASCENDING)], unique=True),
        IndexModel([("expiresAt", ASCENDING)]),
        IndexModel([("createdAt", DESCENDING)])
    ])
    
    # Audit logs collection indexes
    await database.audit_logs.create_indexes([
        IndexModel([("userId", ASCENDING)]),
        IndexModel([("action", ASCENDING)]),
        IndexModel([("resourceType", ASCENDING)]),
        IndexModel([("timestamp", DESCENDING)]),
        IndexModel([("ipAddress", ASCENDING)])
    ])
    
    # Notifications collection indexes
    await database.notifications.create_indexes([
        IndexModel([("userId", ASCENDING)]),
        IndexModel([("type", ASCENDING)]),
        IndexModel([("isRead", ASCENDING)]),
        IndexModel([("createdAt", DESCENDING)]),
        IndexModel([("userId", ASCENDING), ("isRead", ASCENDING)])
    ])
    
    logger.info("Database indexes created successfully")

# Collection getters
def get_collection(collection_name: str):
    """Get a specific collection"""
    return get_database()[collection_name]

# Collection names
COLLECTIONS = {
    "users": "users",
    "zones": "zones", 
    "divisions": "divisions",
    "stations": "stations",
    "vendors": "vendors",
    "manufacturers": "manufacturers",
    "fitting_categories": "fitting_categories",
    "fitting_types": "fitting_types",
    "supply_orders": "supply_orders",
    "fitting_batches": "fitting_batches",
    "qr_codes": "qr_codes",
    "fitting_installations": "fitting_installations",
    "inspections": "inspections",
    "maintenance_records": "maintenance_records",
    "qr_scan_logs": "qr_scan_logs",
    "ai_analysis_reports": "ai_analysis_reports",
    "portal_integrations": "portal_integrations",
    "user_sessions": "user_sessions",
    "audit_logs": "audit_logs",
    "notifications": "notifications"
}
