"""
QR code service for business logic
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog
import qrcode
from io import BytesIO
import base64

from app.config.database import get_collection
from app.config.settings import get_settings
from app.utils.security import generate_qr_code_data

logger = structlog.get_logger()
settings = get_settings()

class QRCodeService:
    """QR code service class"""
    
    @staticmethod
    async def generate_qr_codes_for_batch(
        fitting_batch_id: str, 
        quantity: int, 
        marking_machine_id: str, 
        marking_operator_id: str
    ) -> List[Dict[str, Any]]:
        """Generate QR codes for a fitting batch"""
        try:
            # Verify batch exists
            batches_collection = get_collection("fitting_batches")
            batch = await batches_collection.find_one({"_id": fitting_batch_id})
            
            if not batch:
                raise ValueError("Fitting batch not found")
            
            # Generate QR codes
            qr_codes = []
            qr_codes_collection = get_collection("qr_codes")
            
            for i in range(quantity):
                sequence_number = i + 1
                qr_data = generate_qr_code_data(fitting_batch_id, sequence_number)
                
                # Generate QR code image
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=settings.QR_CODE_SIZE,
                    border=settings.QR_CODE_BORDER,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                # Create QR code image
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convert to base64
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                # Create QR code document
                qr_code_doc = {
                    "qrCode": qr_data,
                    "fittingBatchId": fitting_batch_id,
                    "sequenceNumber": sequence_number,
                    "status": "generated",
                    "generatedAt": datetime.utcnow(),
                    "markingMachineId": marking_machine_id,
                    "markingOperatorId": marking_operator_id,
                    "qrImageBase64": qr_image_base64,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
                
                # Insert QR code
                result = await qr_codes_collection.insert_one(qr_code_doc)
                qr_code_doc["_id"] = result.inserted_id
                qr_codes.append(qr_code_doc)
            
            # Update batch with QR code count
            await batches_collection.update_one(
                {"_id": fitting_batch_id},
                {"$set": {"qrCodeCount": quantity, "updatedAt": datetime.utcnow()}}
            )
            
            logger.info(f"Generated {quantity} QR codes for batch {fitting_batch_id}")
            return qr_codes
            
        except Exception as e:
            logger.error("QR code generation error", error=str(e))
            raise
    
    @staticmethod
    async def get_qr_code_details(qr_code: str) -> Optional[Dict[str, Any]]:
        """Get QR code details with related information"""
        try:
            qr_codes_collection = get_collection("qr_codes")
            qr_code_doc = await qr_codes_collection.find_one({"qrCode": qr_code})
            
            if not qr_code_doc:
                return None
            
            # Get related information
            batch_id = qr_code_doc.get("fittingBatchId")
            batch = None
            fitting_type = None
            installation = None
            last_inspection = None
            
            if batch_id:
                # Get batch information
                batches_collection = get_collection("fitting_batches")
                batch = await batches_collection.find_one({"_id": batch_id})
                
                if batch:
                    # Get fitting type information
                    supply_order_id = batch.get("supplyOrderId")
                    if supply_order_id:
                        supply_orders_collection = get_collection("supply_orders")
                        supply_order = await supply_orders_collection.find_one({"_id": supply_order_id})
                        
                        if supply_order and supply_order.get("items"):
                            item_index = qr_code_doc.get("supplyOrderItemIndex", 0)
                            if item_index < len(supply_order["items"]):
                                fitting_type_id = supply_order["items"][item_index].get("fittingTypeId")
                                if fitting_type_id:
                                    fitting_types_collection = get_collection("fitting_types")
                                    fitting_type = await fitting_types_collection.find_one({"_id": fitting_type_id})
            
            # Get installation information
            installations_collection = get_collection("fitting_installations")
            installation = await installations_collection.find_one({"qrCodeId": qr_code_doc["_id"]})
            
            # Get last inspection
            inspections_collection = get_collection("inspections")
            last_inspection = await inspections_collection.find_one(
                {"qrCodeId": qr_code_doc["_id"]},
                sort=[("inspectionDate", -1)]
            )
            
            return {
                "qrCode": qr_code_doc,
                "batch": batch,
                "fittingType": fitting_type,
                "installation": installation,
                "lastInspection": last_inspection
            }
            
        except Exception as e:
            logger.error("Get QR code details error", error=str(e))
            return None
    
    @staticmethod
    async def log_qr_scan(
        qr_code_id: str,
        scanned_by: str,
        scan_purpose: str,
        scan_location: Optional[str] = None,
        scan_coordinates: Optional[Dict[str, float]] = None,
        device_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Log QR code scan"""
        try:
            scan_logs_collection = get_collection("qr_scan_logs")
            
            scan_log = {
                "qrCodeId": qr_code_id,
                "scannedBy": scanned_by,
                "scanPurpose": scan_purpose,
                "scanLocation": scan_location,
                "scanCoordinates": scan_coordinates,
                "deviceInfo": device_info,
                "scanDate": datetime.utcnow(),
                "createdAt": datetime.utcnow()
            }
            
            result = await scan_logs_collection.insert_one(scan_log)
            scan_log["_id"] = result.inserted_id
            
            logger.info(f"Logged QR scan for {qr_code_id} by {scanned_by}")
            return scan_log
            
        except Exception as e:
            logger.error("QR scan logging error", error=str(e))
            raise
    
    @staticmethod
    async def verify_qr_code(qr_code_id: str, verification_status: str, print_quality_score: Optional[float] = None) -> bool:
        """Verify QR code"""
        try:
            qr_codes_collection = get_collection("qr_codes")
            
            update_data = {
                "verificationStatus": verification_status,
                "verifiedAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            if print_quality_score is not None:
                update_data["printQualityScore"] = print_quality_score
            
            result = await qr_codes_collection.update_one(
                {"_id": qr_code_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error("QR code verification error", error=str(e))
            return False
