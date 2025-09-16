# QR Track Fittings System - API Documentation

## Overview

The QR Track Fittings System is a comprehensive FastAPI backend for Indian Railways' AI-based QR Code Track Fittings management system. This system manages 10 crore Elastic Rail Clips, 5 crore liners, and 8.5 crore rail pads annually with QR code tracking, AI-powered analytics, and integration with UDM and TMS portals.

## Base URL

```
http://localhost:8000/api
```

## Authentication

All API endpoints (except login) require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error information"
}
```

### Paginated Response
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 100,
      "pages": 10,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

## API Endpoints

### 1. Authentication & User Management (7 APIs)

#### POST /api/auth/login
User login endpoint.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "deviceInfo": {
    "type": "mobile",
    "os": "Android",
    "version": "10.0"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_id",
      "name": "John Doe",
      "email": "user@example.com",
      "role": "inspector"
    },
    "token": "jwt_token_here",
    "expiresAt": "2025-09-16T10:00:00Z"
  }
}
```

#### POST /api/auth/logout
User logout endpoint.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

#### POST /api/auth/refresh
Refresh access token.

**Request Body:**
```json
{
  "refreshToken": "refresh_token_here"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "new_jwt_token",
    "expiresAt": "2025-09-16T11:00:00Z"
  }
}
```

#### GET /api/users
Get users with pagination and filters.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 10, max: 100)
- `search` (string): Search term
- `role` (string): Filter by role
- `status` (string): Filter by status
- `zoneId` (string): Filter by zone ID
- `divisionId` (string): Filter by division ID
- `stationId` (string): Filter by station ID

**Response:**
```json
{
  "success": true,
  "data": {
    "users": [...],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 100,
      "pages": 10
    }
  }
}
```

#### POST /api/users
Create a new user.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "inspector",
  "phone": "9876543210",
  "zoneId": "zone_id"
}
```

#### PUT /api/users/:id
Update user information.

**Request Body:**
```json
{
  "name": "Updated Name",
  "phone": "9876543211",
  "status": "active"
}
```

#### DELETE /api/users/:id
Soft delete a user.

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

### 2. Hierarchy Management (9 APIs)

#### GET /api/zones
Get zones with pagination and filters.

**Query Parameters:**
- `page`, `limit`, `search`, `status`, `sortBy`, `sortOrder`

#### POST /api/zones
Create a new zone.

**Request Body:**
```json
{
  "name": "Southern Railway",
  "code": "SR",
  "description": "Southern Railway Zone",
  "headquarters": "Chennai",
  "coordinates": {
    "lat": 13.0827,
    "lng": 80.2707
  }
}
```

#### GET /api/divisions
Get divisions with pagination and filters.

#### POST /api/divisions
Create a new division.

**Request Body:**
```json
{
  "name": "Chennai Division",
  "code": "CD",
  "zoneId": "zone_id",
  "description": "Chennai Division",
  "headquarters": "Chennai"
}
```

#### GET /api/stations
Get stations with pagination and filters.

#### POST /api/stations
Create a new station.

**Request Body:**
```json
{
  "name": "Chennai Central",
  "code": "MAS",
  "divisionId": "division_id",
  "description": "Chennai Central Station",
  "stationType": "Terminal",
  "coordinates": {
    "lat": 13.0827,
    "lng": 80.2707
  },
  "platformCount": 12
}
```

#### GET /api/vendors
Get vendors with pagination and filters.

#### POST /api/vendors
Create a new vendor.

**Request Body:**
```json
{
  "name": "ABC Railways Supplies",
  "code": "ARS",
  "gstNumber": "29ABCDE1234F1Z5",
  "contactInfo": {
    "email": "contact@abc.com",
    "phone": "9876543210"
  },
  "address": "123 Railway Street",
  "city": "Chennai",
  "state": "Tamil Nadu",
  "pincode": "600001"
}
```

#### GET /api/manufacturers
Get manufacturers with pagination and filters.

#### POST /api/manufacturers
Create a new manufacturer.

**Request Body:**
```json
{
  "name": "Steel Works Ltd",
  "code": "SWL",
  "licenseNumber": "MFG123456",
  "contactInfo": {
    "email": "info@steelworks.com",
    "phone": "9876543211"
  },
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001"
}
```

### 3. Fitting & Supply Management (10 APIs)

#### GET /api/fitting-categories
Get fitting categories with pagination and filters.

#### POST /api/fitting-categories
Create a new fitting category.

**Request Body:**
```json
{
  "name": "Elastic Rail Clip",
  "code": "ERC",
  "description": "Elastic Rail Clip for track fastening",
  "specifications": {
    "material": "Spring Steel",
    "dimensions": {
      "length": 150,
      "width": 25,
      "thickness": 8
    },
    "weight": 0.5,
    "tensileStrength": 1200
  },
  "warrantyPeriodMonths": 24,
  "standardCode": "IS:1234"
}
```

#### GET /api/fitting-types
Get fitting types with pagination and filters.

#### POST /api/fitting-types
Create a new fitting type.

**Request Body:**
```json
{
  "name": "Type A Rail Clip",
  "model": "A-100",
  "categoryId": "category_id",
  "description": "Type A Elastic Rail Clip",
  "manufacturerId": "manufacturer_id",
  "partNumber": "ERC-A100",
  "specifications": {
    "material": "Spring Steel",
    "dimensions": {
      "length": 150,
      "width": 25,
      "thickness": 8
    }
  }
}
```

#### GET /api/supply-orders
Get supply orders with pagination and filters.

#### POST /api/supply-orders
Create a new supply order.

**Request Body:**
```json
{
  "orderNumber": "SO-2025-001",
  "vendorId": "vendor_id",
  "manufacturerId": "manufacturer_id",
  "orderDate": "2025-01-01T00:00:00Z",
  "expectedDeliveryDate": "2025-02-01T00:00:00Z",
  "items": [
    {
      "fittingTypeId": "fitting_type_id",
      "quantity": 1000,
      "unitPrice": 50.00,
      "totalPrice": 50000.00,
      "deliveryDate": "2025-02-01T00:00:00Z"
    }
  ],
  "totalAmount": 50000.00,
  "currency": "INR",
  "priority": "normal"
}
```

#### PUT /api/supply-orders/:id/status
Update supply order status.

**Request Body:**
```json
{
  "status": "delivered",
  "actualDeliveryDate": "2025-02-01T00:00:00Z",
  "remarks": "Delivered on time"
}
```

#### GET /api/fitting-batches
Get fitting batches with pagination and filters.

#### POST /api/fitting-batches
Create a new fitting batch.

**Request Body:**
```json
{
  "batchNumber": "BATCH-2025-001",
  "supplyOrderId": "supply_order_id",
  "supplyOrderItemIndex": 0,
  "quantity": 500,
  "manufacturerId": "manufacturer_id",
  "manufacturingDate": "2025-01-15T00:00:00Z",
  "qualityGrade": "A",
  "remarks": "High quality batch"
}
```

#### PUT /api/fitting-batches/:id/quality-documents
Upload quality documents for a batch.

**Request:** Multipart form data with certificate and test report files.

### 4. QR Code & Installation (7 APIs)

#### POST /api/qr-codes/generate-batch
Generate QR codes for a fitting batch.

**Request Body:**
```json
{
  "fittingBatchId": "batch_id",
  "quantity": 500,
  "markingMachineId": "LASER-001",
  "markingOperatorId": "operator_id"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "qrCodes": [...],
    "batchSummary": {
      "totalGenerated": 500,
      "batchId": "batch_id"
    }
  }
}
```

#### GET /api/qr-codes/:qrCode
Get QR code details with related information.

**Response:**
```json
{
  "success": true,
  "data": {
    "qrCode": {...},
    "batch": {...},
    "fittingType": {...},
    "installation": {...},
    "lastInspection": {...}
  }
}
```

#### POST /api/qr-codes/:qrCode/scan
Log QR code scan.

**Request Body:**
```json
{
  "scanLocation": "Track Section A",
  "scanCoordinates": {
    "lat": 13.0827,
    "lng": 80.2707
  },
  "scanPurpose": "inspection",
  "deviceInfo": {
    "type": "mobile",
    "os": "Android"
  }
}
```

#### PUT /api/qr-codes/:id/verify
Verify QR code quality.

**Request Body:**
```json
{
  "verificationStatus": "verified",
  "printQualityScore": 0.95
}
```

#### POST /api/installations
Record fitting installation.

**Request Body:**
```json
{
  "qrCodeId": "qr_code_id",
  "zoneId": "zone_id",
  "trackSection": "Section A-1",
  "kilometerPost": "KM 10.5",
  "installationCoordinates": {
    "lat": 13.0827,
    "lng": 80.2707
  }
}
```

#### GET /api/installations
Get installations with pagination and filters.

#### PUT /api/installations/:id/status
Update installation status.

**Request Body:**
```json
{
  "status": "maintenance_due",
  "remarks": "Routine maintenance required"
}
```

### 5. Inspection & Maintenance (7 APIs)

#### GET /api/inspections
Get inspections with pagination and filters.

#### POST /api/inspections
Create a new inspection.

**Request Body:**
```json
{
  "qrCodeId": "qr_code_id",
  "inspectionType": "routine",
  "checklistData": [
    {
      "item": "Visual condition check",
      "status": "pass",
      "value": 95,
      "unit": "percentage"
    }
  ],
  "visualCondition": "good",
  "photos": ["base64_image_1", "base64_image_2"],
  "recommendation": "Continue monitoring"
}
```

#### PUT /api/inspections/:id/complete
Complete an inspection.

**Request Body:**
```json
{
  "recommendation": "pass",
  "nextInspectionDue": "2025-12-15T00:00:00Z",
  "remarks": "All parameters within limits"
}
```

#### GET /api/inspections/:id/photos/:photoIndex
Get inspection photo by index.

**Response:** Binary image data with appropriate content-type header.

#### GET /api/maintenance-records
Get maintenance records with pagination and filters.

#### POST /api/maintenance-records
Create a new maintenance record.

**Request Body:**
```json
{
  "qrCodeId": "qr_code_id",
  "maintenanceType": "corrective",
  "workDescription": "Replaced worn rail clip",
  "partsReplaced": [
    {
      "part": "rail_clip",
      "quantity": 1,
      "cost": 50.00
    }
  ],
  "beforePhotos": ["base64_image_1"],
  "afterPhotos": ["base64_image_2"],
  "cost": 100.00
}
```

#### PUT /api/maintenance-records/:id/quality-check
Update maintenance record quality check.

**Request Body:**
```json
{
  "qualityCheckPassed": true,
  "nextMaintenanceDue": "2026-03-15T00:00:00Z"
}
```

### 6. AI & Analytics (9 APIs)

#### POST /api/ai-analysis/analyze
Analyze QR code data using AI.

**Request Body:**
```json
{
  "qrCodeId": "qr_code_id",
  "analysisType": "predictive",
  "inputData": {
    "inspectionHistory": [...],
    "maintenanceHistory": [...],
    "environmentalData": {...}
  }
}
```

#### GET /api/ai-analysis/reports
Get AI analysis reports with pagination and filters.

#### POST /api/ai-analysis/bulk-predict
Perform bulk AI analysis.

**Request Body:**
```json
{
  "filters": {
    "zoneId": "zone_id",
    "fittingTypeId": "fitting_type_id"
  },
  "analysisType": "lifecycle"
}
```

#### GET /api/reports/dashboard
Get dashboard report.

**Query Parameters:**
- `zoneId`, `divisionId`, `dateRange`

**Response:**
```json
{
  "success": true,
  "data": {
    "totalFittings": 50000,
    "activeInstallations": 48000,
    "pendingInspections": 500,
    "maintenanceDue": 200,
    "riskDistribution": {
      "low": 40000,
      "medium": 8000,
      "high": 1500,
      "critical": 500
    }
  }
}
```

#### GET /api/reports/performance
Get performance report.

#### GET /api/reports/inventory
Get inventory report.

#### GET /api/analytics/performance-metrics
Get performance metrics.

#### GET /api/analytics/quality-trends
Get quality trends analysis.

### 7. Integration & Mobile (6 APIs)

#### POST /api/integrations/udm/sync
Sync data with UDM portal.

**Request Body:**
```json
{
  "recordType": "supply_order",
  "recordIds": ["order_id_1", "order_id_2"]
}
```

#### POST /api/integrations/tms/sync
Sync data with TMS portal.

#### GET /api/integrations/status
Get integration status.

#### GET /api/mobile/sync/offline-data
Get offline data for mobile sync.

#### POST /api/mobile/sync/upload
Upload offline data from mobile.

#### GET /api/mobile/qr/:qrCode/offline-data
Get QR code offline data for mobile.

### 8. Notifications & Search (5 APIs)

#### GET /api/notifications
Get notifications with pagination and filters.

#### PUT /api/notifications/:id/read
Mark notification as read.

#### POST /api/notifications/bulk-read
Mark multiple notifications as read.

#### GET /api/search/fittings
Search fittings with advanced filters.

**Query Parameters:**
- `query`: Search query
- `filters`: JSON string of filters
- `sort`: Sort by relevance, date, name
- `page`, `limit`

#### GET /api/search/locations
Search locations.

### 9. Export & File Management (5 APIs)

#### POST /api/export/report
Export report in various formats.

**Request Body:**
```json
{
  "reportType": "inspection_report",
  "filters": {...},
  "format": "pdf",
  "includePhotos": true
}
```

#### GET /api/export/:exportId/status
Get export status.

#### GET /api/export/:exportId/download
Download exported file.

#### POST /api/upload/images
Upload images.

**Request:** Multipart form data with image files.

#### GET /api/images/:imageId
Get image by ID.

### 10. Administration (5 APIs)

#### GET /api/admin/system-health
Get system health status.

#### POST /api/admin/backup
Create system backup.

#### GET /api/admin/audit-logs
Get audit logs with pagination.

#### GET /api/config/app-settings
Get application settings.

#### PUT /api/config/app-settings
Update application settings.

### 11. Batch Operations (2 APIs)

#### POST /api/batch/bulk-inspection
Schedule bulk inspections.

**Request Body:**
```json
{
  "qrCodeIds": ["qr1", "qr2", "qr3"],
  "inspectionType": "routine",
  "scheduledDate": "2025-09-20T00:00:00Z",
  "assignedInspector": "inspector_id"
}
```

#### POST /api/batch/bulk-maintenance
Schedule bulk maintenance.

**Request Body:**
```json
{
  "filters": {
    "zoneId": "zone_id",
    "status": "maintenance_due"
  },
  "maintenanceType": "preventive",
  "scheduledDate": "2025-09-25T00:00:00Z"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

## Rate Limiting

- Default rate limit: 100 requests per minute per user
- Burst limit: 200 requests per minute
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Pagination

All list endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 100)
- `sortBy`: Sort field (default: varies by endpoint)
- `sortOrder`: Sort order - "asc" or "desc" (default: "desc")

## Filtering and Search

Most list endpoints support:
- Text search across relevant fields
- Status filtering
- Date range filtering
- Hierarchical filtering (zone → division → station)

## File Upload

For file uploads (images, documents):
- Maximum file size: 10MB
- Allowed image types: JPEG, PNG, WebP
- Files are stored in MongoDB GridFS
- Base64 encoding supported for mobile clients

## WebSocket Support

Real-time features available via WebSocket:
- Live notifications
- Real-time status updates
- Progress tracking for long-running operations

## SDK and Client Libraries

Official client libraries available for:
- Python
- JavaScript/TypeScript
- Java
- C#

## Support

For API support and questions:
- Documentation: `/docs` (Swagger UI)
- Alternative docs: `/redoc`
- Health check: `/health`
