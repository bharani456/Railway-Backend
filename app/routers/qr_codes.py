"""
QR codes router - Task 8: Batch and QR Code Management
APIs: POST /api/qr-codes/generate-batch, GET /api/qr-codes/:qrCode, 
      POST /api/qr-codes/:qrCode/scan, PUT /api/qr-codes/:id/verify
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Optional, List
from datetime import datetime
import structlog
import qrcode
from io import BytesIO
import base64

from app.models.base import APIResponse, PaginatedResponse, Coordinates
from app.utils.security import verify_token, check_permissions, generate_qr_code_data
from app.config.database import get_collection
from app.config.settings import get_settings

logger = structlog.get_logger()
router = APIRouter()
settings = get_settings()

@router.post("/generate-batch", response_model=APIResponse)
async def generate_batch_qr_codes(
    batch_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Generate QR codes for a fitting batch
    
    Input: {"fittingBatchId": "batch_id", "quantity": 500, "markingMachineId": "LASER-001", "markingOperatorId": "operator_id"}
    Output: {"success": true, "data": {"qrCodes": [...generatedQRCodeObjects], "batchSummary": {"totalGenerated": 500, "batchId": "batch_id"}}}
    """
    try:
        if not check_permissions(current_user["role"], "qr_codes"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        fitting_batch_id = batch_data.get("fittingBatchId")
        quantity = batch_data.get("quantity", 1)
        marking_machine_id = batch_data.get("markingMachineId")
        marking_operator_id = batch_data.get("markingOperatorId")
        
        if not fitting_batch_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fitting batch ID is required")
        
        if quantity <= 0 or quantity > 10000:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be between 1 and 10000")
        
        # Verify batch exists
        batches_collection = get_collection("fitting_batches")
        batch = await batches_collection.find_one({"_id": fitting_batch_id})
        if not batch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fitting batch not found")
        
        # Generate QR codes
        qr_codes_collection = get_collection("qr_codes")
        generated_qr_codes = []
        
        for i in range(quantity):
            qr_data = generate_qr_code_data(fitting_batch_id, i + 1)
            
            # Generate QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=settings.QR_CODE_SIZE,
                border=settings.QR_CODE_BORDER,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            # Create QR code document
            qr_doc = {
                "qrCode": qr_data,
                "fittingBatchId": fitting_batch_id,
                "sequenceNumber": i + 1,
                "status": "generated",
                "markingMachineId": marking_machine_id,
                "markingOperatorId": marking_operator_id,
                "qrCodeImage": img_str,
                "generatedAt": datetime.utcnow(),
                "createdBy": current_user["userId"],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            result = await qr_codes_collection.insert_one(qr_doc)
            qr_doc["id"] = str(result.inserted_id)
            generated_qr_codes.append(qr_doc)
        
        # Update batch status
        await batches_collection.update_one(
            {"_id": fitting_batch_id},
            {
                "$set": {
                    "qrCodesGenerated": quantity,
                    "qrGenerationDate": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        logger.info(
            "QR codes generated successfully",
            user_id=current_user["userId"],
            batch_id=fitting_batch_id,
            quantity=quantity
        )
        
        return APIResponse(
            success=True,
            data={
                "qrCodes": generated_qr_codes,
                "batchSummary": {
                    "totalGenerated": quantity,
                    "batchId": fitting_batch_id,
                    "generatedAt": datetime.utcnow().isoformat() + "Z"
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate QR codes", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate QR codes")

@router.get("/{qr_code}", response_model=APIResponse)
async def get_qr_code(
    qr_code: str,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Get QR code information
    
    Input: QR code string in URL
    Output: {"success": true, "data": {"qrCode": {...}, "batch": {...}, "fittingType": {...}, "installation": {...}, "lastInspection": {...}}}
    """
    try:
        if not check_permissions(current_user["role"], "qr_codes"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        qr_codes_collection = get_collection("qr_codes")
        qr_code_doc = await qr_codes_collection.find_one({"qrCode": qr_code})
        
        if not qr_code_doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR code not found")
        
        # Get related data
        batch_data = None
        fitting_type_data = None
        installation_data = None
        last_inspection_data = None
        
        # Get batch information
        if qr_code_doc.get("fittingBatchId"):
            batches_collection = get_collection("fitting_batches")
            batch = await batches_collection.find_one({"_id": qr_code_doc["fittingBatchId"]})
            if batch:
                batch_data = {k: v for k, v in batch.items() if k != "_id"}
                batch_data["id"] = str(batch["_id"])
        
        # Get fitting type information
        if batch_data and batch_data.get("fittingTypeId"):
            fitting_types_collection = get_collection("fitting_types")
            fitting_type = await fitting_types_collection.find_one({"_id": batch_data["fittingTypeId"]})
            if fitting_type:
                fitting_type_data = {k: v for k, v in fitting_type.items() if k != "_id"}
                fitting_type_data["id"] = str(fitting_type["_id"])
        
        # Get installation information
        installations_collection = get_collection("fitting_installations")
        installation = await installations_collection.find_one({"qrCodeId": str(qr_code_doc["_id"])})
        if installation:
            installation_data = {k: v for k, v in installation.items() if k != "_id"}
            installation_data["id"] = str(installation["_id"])
        
        # Get last inspection
        inspections_collection = get_collection("inspections")
        last_inspection = await inspections_collection.find_one(
            {"qrCodeId": str(qr_code_doc["_id"])},
            sort=[("inspectionDate", -1)]
        )
        if last_inspection:
            last_inspection_data = {k: v for k, v in last_inspection.items() if k != "_id"}
            last_inspection_data["id"] = str(last_inspection["_id"])
        
        # Format QR code data
        qr_code_data = {k: v for k, v in qr_code_doc.items() if k != "_id"}
        qr_code_data["id"] = str(qr_code_doc["_id"])
        
        logger.info(
            "QR code retrieved successfully",
            user_id=current_user["userId"],
            qr_code=qr_code
        )
        
        return APIResponse(
            success=True,
            data={
                "qrCode": qr_code_data,
                "batch": batch_data,
                "fittingType": fitting_type_data,
                "installation": installation_data,
                "lastInspection": last_inspection_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get QR code", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve QR code")

@router.post("/{qr_code}/scan", response_model=APIResponse)
async def scan_qr_code(
    qr_code: str,
    scan_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Log QR code scan
    
    Input: {"scanLocation": "Track Section A", "scanCoordinates": {"lat": 13.0827, "lng": 80.2707}, "scanPurpose": "inspection", "deviceInfo": {...}}
    Output: {"success": true, "data": {"scanLog": {...createdScanLogObject}}}
    """
    try:
        if not check_permissions(current_user["role"], "qr_codes"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Verify QR code exists
        qr_codes_collection = get_collection("qr_codes")
        qr_code_doc = await qr_codes_collection.find_one({"qrCode": qr_code})
        
        if not qr_code_doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR code not found")
        
        # Create scan log
        scan_logs_collection = get_collection("qr_scan_logs")
        scan_log_doc = {
            "qrCodeId": str(qr_code_doc["_id"]),
            "qrCode": qr_code,
            "scannedBy": current_user["userId"],
            "scanLocation": scan_data.get("scanLocation"),
            "scanCoordinates": scan_data.get("scanCoordinates"),
            "scanPurpose": scan_data.get("scanPurpose", "general"),
            "deviceInfo": scan_data.get("deviceInfo", {}),
            "ipAddress": request.client.host if request.client else None,
            "userAgent": request.headers.get("user-agent"),
            "scanDate": datetime.utcnow(),
            "createdAt": datetime.utcnow()
        }
        
        result = await scan_logs_collection.insert_one(scan_log_doc)
        scan_log_doc["id"] = str(result.inserted_id)
        
        # Update QR code last scan time
        await qr_codes_collection.update_one(
            {"_id": qr_code_doc["_id"]},
            {
                "$set": {
                    "lastScannedAt": datetime.utcnow(),
                    "lastScannedBy": current_user["userId"],
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        logger.info(
            "QR code scanned successfully",
            user_id=current_user["userId"],
            qr_code=qr_code,
            scan_purpose=scan_data.get("scanPurpose")
        )
        
        return APIResponse(
            success=True,
            data={"scanLog": scan_log_doc}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to scan QR code", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to scan QR code")

@router.put("/{qr_id}/verify", response_model=APIResponse)
async def verify_qr_code(
    qr_id: str,
    verification_data: dict,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    """
    Verify QR code quality and status
    
    Input: {"verificationStatus": "verified", "printQualityScore": 0.95}
    Output: {"success": true, "data": {"qrCode": {...updatedQRCodeObject}}}
    """
    try:
        if not check_permissions(current_user["role"], "qr_codes"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        verification_status = verification_data.get("verificationStatus")
        print_quality_score = verification_data.get("printQualityScore")
        remarks = verification_data.get("remarks")
        
        if verification_status not in ["verified", "rejected", "needs_reprint"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification status")
        
        if print_quality_score is not None and (print_quality_score < 0 or print_quality_score > 1):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Print quality score must be between 0 and 1")
        
        # Update QR code
        qr_codes_collection = get_collection("qr_codes")
        update_data = {
            "verificationStatus": verification_status,
            "verifiedAt": datetime.utcnow(),
            "verifiedBy": current_user["userId"],
            "updatedAt": datetime.utcnow()
        }
        
        if print_quality_score is not None:
            update_data["printQualityScore"] = print_quality_score
        
        if remarks:
            update_data["verificationRemarks"] = remarks
        
        if verification_status == "verified":
            update_data["status"] = "verified"
        elif verification_status == "rejected":
            update_data["status"] = "rejected"
        elif verification_status == "needs_reprint":
            update_data["status"] = "needs_reprint"
        
        await qr_codes_collection.update_one(
            {"_id": qr_id},
            {"$set": update_data}
        )
        
        # Get updated QR code
        updated_qr_code = await qr_codes_collection.find_one({"_id": qr_id})
        updated_qr_code_dict = {k: v for k, v in updated_qr_code.items() if k != "_id"}
        updated_qr_code_dict["id"] = str(updated_qr_code["_id"])
        
        logger.info(
            "QR code verified successfully",
            user_id=current_user["userId"],
            qr_id=qr_id,
            verification_status=verification_status
        )
        
        return APIResponse(
            success=True,
            data={"qrCode": updated_qr_code_dict}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to verify QR code", error=str(e), user_id=current_user.get("userId"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to verify QR code")
