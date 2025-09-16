"""
Test configuration and fixtures
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app
from app.config.database import get_database
from app.config.settings import get_settings

# Test database configuration
TEST_DATABASE_URL = "mongodb://localhost:27017"
TEST_DATABASE_NAME = "qr_track_fittings_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create test database connection"""
    client = AsyncIOMotorClient(TEST_DATABASE_URL)
    db = client[TEST_DATABASE_NAME]
    yield db
    # Cleanup
    await client.drop_database(TEST_DATABASE_NAME)
    client.close()

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
async def test_user(test_db):
    """Create a test user"""
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "passwordHash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.sK2",  # password123
        "role": "admin",
        "isActive": True,
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z",
        "status": "active"
    }
    
    result = await test_db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user"""
    # This would normally contain a valid JWT token
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
async def test_zone(test_db):
    """Create a test zone"""
    zone_data = {
        "name": "Test Zone",
        "code": "TZ",
        "description": "Test zone for testing",
        "status": "active",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z"
    }
    
    result = await test_db.zones.insert_one(zone_data)
    zone_data["_id"] = result.inserted_id
    return zone_data

@pytest.fixture
async def test_division(test_db, test_zone):
    """Create a test division"""
    division_data = {
        "name": "Test Division",
        "code": "TD",
        "zoneId": test_zone["_id"],
        "description": "Test division for testing",
        "status": "active",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z"
    }
    
    result = await test_db.divisions.insert_one(division_data)
    division_data["_id"] = result.inserted_id
    return division_data

@pytest.fixture
async def test_station(test_db, test_division):
    """Create a test station"""
    station_data = {
        "name": "Test Station",
        "code": "TS",
        "divisionId": test_division["_id"],
        "description": "Test station for testing",
        "status": "active",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z"
    }
    
    result = await test_db.stations.insert_one(station_data)
    station_data["_id"] = result.inserted_id
    return station_data

@pytest.fixture
async def test_fitting_category(test_db):
    """Create a test fitting category"""
    category_data = {
        "name": "Test Fitting Category",
        "code": "TFC",
        "description": "Test fitting category for testing",
        "status": "active",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z"
    }
    
    result = await test_db.fitting_categories.insert_one(category_data)
    category_data["_id"] = result.inserted_id
    return category_data

@pytest.fixture
async def test_fitting_type(test_db, test_fitting_category):
    """Create a test fitting type"""
    fitting_type_data = {
        "name": "Test Fitting Type",
        "model": "TFT-001",
        "categoryId": test_fitting_category["_id"],
        "description": "Test fitting type for testing",
        "status": "active",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z"
    }
    
    result = await test_db.fitting_types.insert_one(fitting_type_data)
    fitting_type_data["_id"] = result.inserted_id
    return fitting_type_data

@pytest.fixture
async def test_vendor(test_db):
    """Create a test vendor"""
    vendor_data = {
        "name": "Test Vendor",
        "code": "TV",
        "contactInfo": {
            "email": "vendor@example.com",
            "phone": "9876543210"
        },
        "city": "Test City",
        "state": "Test State",
        "pincode": "123456",
        "status": "active",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z"
    }
    
    result = await test_db.vendors.insert_one(vendor_data)
    vendor_data["_id"] = result.inserted_id
    return vendor_data

@pytest.fixture
async def test_supply_order(test_db, test_vendor, test_fitting_type):
    """Create a test supply order"""
    supply_order_data = {
        "orderNumber": "SO-2025-001",
        "vendorId": test_vendor["_id"],
        "orderDate": "2025-01-01T00:00:00Z",
        "items": [{
            "fittingTypeId": test_fitting_type["_id"],
            "quantity": 100,
            "unitPrice": 50.00,
            "totalPrice": 5000.00
        }],
        "totalAmount": 5000.00,
        "status": "pending",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z"
    }
    
    result = await test_db.supply_orders.insert_one(supply_order_data)
    supply_order_data["_id"] = result.inserted_id
    return supply_order_data

@pytest.fixture
async def test_fitting_batch(test_db, test_supply_order):
    """Create a test fitting batch"""
    batch_data = {
        "batchNumber": "BATCH-2025-001",
        "supplyOrderId": test_supply_order["_id"],
        "supplyOrderItemIndex": 0,
        "quantity": 100,
        "manufacturingDate": "2025-01-01T00:00:00Z",
        "status": "manufactured",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z"
    }
    
    result = await test_db.fitting_batches.insert_one(batch_data)
    batch_data["_id"] = result.inserted_id
    return batch_data

@pytest.fixture
async def test_qr_code(test_db, test_fitting_batch):
    """Create a test QR code"""
    qr_code_data = {
        "qrCode": "QR_TEST_001",
        "fittingBatchId": test_fitting_batch["_id"],
        "sequenceNumber": 1,
        "status": "generated",
        "generatedAt": "2025-01-01T00:00:00Z",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z"
    }
    
    result = await test_db.qr_codes.insert_one(qr_code_data)
    qr_code_data["_id"] = result.inserted_id
    return qr_code_data

@pytest.fixture
async def test_installation(test_db, test_qr_code, test_zone):
    """Create a test installation"""
    installation_data = {
        "qrCodeId": test_qr_code["_id"],
        "zoneId": test_zone["_id"],
        "trackSection": "Section A-1",
        "kilometerPost": "KM 10.5",
        "installationCoordinates": {"lat": 13.0827, "lng": 80.2707},
        "installationDate": "2025-01-01T00:00:00Z",
        "status": "installed",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z"
    }
    
    result = await test_db.fitting_installations.insert_one(installation_data)
    installation_data["_id"] = result.inserted_id
    return installation_data

# Convenience fixtures for test IDs
@pytest.fixture
def test_user_id(test_user):
    return str(test_user["_id"])

@pytest.fixture
def test_zone_id(test_zone):
    return str(test_zone["_id"])

@pytest.fixture
def test_division_id(test_division):
    return str(test_division["_id"])

@pytest.fixture
def test_station_id(test_station):
    return str(test_station["_id"])

@pytest.fixture
def test_fitting_category_id(test_fitting_category):
    return str(test_fitting_category["_id"])

@pytest.fixture
def test_fitting_type_id(test_fitting_type):
    return str(test_fitting_type["_id"])

@pytest.fixture
def test_vendor_id(test_vendor):
    return str(test_vendor["_id"])

@pytest.fixture
def test_supply_order_id(test_supply_order):
    return str(test_supply_order["_id"])

@pytest.fixture
def test_batch_id(test_fitting_batch):
    return str(test_fitting_batch["_id"])

@pytest.fixture
def test_qr_code(test_qr_code):
    return test_qr_code["qrCode"]

@pytest.fixture
def test_qr_code_id(test_qr_code):
    return str(test_qr_code["_id"])

@pytest.fixture
def test_installation_id(test_installation):
    return str(test_installation["_id"])

@pytest.fixture
async def cleanup_test_data(test_db):
    """Cleanup test data after each test"""
    yield
    # Clean up collections
    collections = [
        "users", "zones", "divisions", "stations", "vendors", "manufacturers",
        "fitting_categories", "fitting_types", "supply_orders", "fitting_batches",
        "qr_codes", "fitting_installations", "inspections", "maintenance_records",
        "qr_scan_logs", "ai_analysis_reports", "portal_integrations",
        "user_sessions", "audit_logs", "notifications"
    ]
    
    for collection_name in collections:
        await test_db[collection_name].delete_many({})
