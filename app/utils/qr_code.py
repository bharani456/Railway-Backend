"""
QR Code generation and processing utilities
"""

import qrcode
from qrcode.image.pil import PilImage
from PIL import Image, ImageDraw, ImageFont
import io
import structlog
from typing import Optional, Tuple

from app.config.settings import get_settings

logger = structlog.get_logger()
settings = get_settings()

def generate_qr_code(
    data: str,
    size: int = None,
    border: int = None,
    error_correction: str = None
) -> bytes:
    """Generate QR code image as bytes"""
    if size is None:
        size = settings.QR_CODE_SIZE
    if border is None:
        border = settings.QR_CODE_BORDER
    if error_correction is None:
        error_correction = settings.QR_CODE_ERROR_CORRECTION
    
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=getattr(qrcode.constants.ERROR_CORRECT_M, error_correction),
            box_size=size,
            border=border,
        )
        
        # Add data
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        output = io.BytesIO()
        qr_image.save(output, format="PNG")
        qr_bytes = output.getvalue()
        
        logger.info(
            "QR code generated",
            data_length=len(data),
            image_size=qr_image.size,
            file_size=len(qr_bytes)
        )
        
        return qr_bytes
        
    except Exception as e:
        logger.error("QR code generation failed", error=str(e))
        raise ValueError("Failed to generate QR code")

def generate_qr_code_with_text(
    data: str,
    text: str,
    size: int = None,
    border: int = None,
    text_size: int = 20
) -> bytes:
    """Generate QR code with text below it"""
    if size is None:
        size = settings.QR_CODE_SIZE
    if border is None:
        border = settings.QR_CODE_BORDER
    
    try:
        # Generate QR code
        qr_bytes = generate_qr_code(data, size, border)
        qr_image = Image.open(io.BytesIO(qr_bytes))
        
        # Calculate dimensions for text
        qr_width, qr_height = qr_image.size
        text_height = text_size + 10  # Add padding
        
        # Create new image with space for text
        total_height = qr_height + text_height
        combined_image = Image.new("RGB", (qr_width, total_height), "white")
        
        # Paste QR code
        combined_image.paste(qr_image, (0, 0))
        
        # Add text
        draw = ImageDraw.Draw(combined_image)
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Calculate text position (centered)
        if font:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
        else:
            text_width = len(text) * 6  # Approximate width
        
        text_x = (qr_width - text_width) // 2
        text_y = qr_height + 5
        
        # Draw text
        draw.text((text_x, text_y), text, fill="black", font=font)
        
        # Convert to bytes
        output = io.BytesIO()
        combined_image.save(output, format="PNG")
        combined_bytes = output.getvalue()
        
        logger.info(
            "QR code with text generated",
            data_length=len(data),
            text=text,
            image_size=combined_image.size,
            file_size=len(combined_bytes)
        )
        
        return combined_bytes
        
    except Exception as e:
        logger.error("QR code with text generation failed", error=str(e))
        raise ValueError("Failed to generate QR code with text")

def validate_qr_code_data(data: str) -> bool:
    """Validate QR code data format"""
    try:
        # Check if data starts with QRTF prefix
        if not data.startswith("QRTF_"):
            return False
        
        # Split data into parts
        parts = data.split("_")
        if len(parts) != 4:
            return False
        
        # Check format: QRTF_{batch_id}_{sequence}_{hash}
        prefix, batch_id, sequence, hash_value = parts
        
        # Validate sequence number (should be 6 digits)
        if not sequence.isdigit() or len(sequence) != 6:
            return False
        
        # Validate hash (should be 8 characters)
        if len(hash_value) != 8:
            return False
        
        return True
        
    except Exception as e:
        logger.error("QR code data validation failed", error=str(e))
        return False

def extract_qr_code_info(data: str) -> dict:
    """Extract information from QR code data"""
    try:
        if not validate_qr_code_data(data):
            raise ValueError("Invalid QR code data format")
        
        parts = data.split("_")
        prefix, batch_id, sequence, hash_value = parts
        
        return {
            "prefix": prefix,
            "batch_id": batch_id,
            "sequence_number": int(sequence),
            "hash": hash_value,
            "is_valid": True
        }
        
    except Exception as e:
        logger.error("QR code info extraction failed", error=str(e))
        return {
            "is_valid": False,
            "error": str(e)
        }

def generate_batch_qr_codes(
    batch_id: str,
    quantity: int,
    start_sequence: int = 1
) -> list:
    """Generate multiple QR codes for a batch"""
    qr_codes = []
    
    try:
        for i in range(quantity):
            sequence_number = start_sequence + i
            qr_data = f"QRTF_{batch_id}_{sequence_number:06d}_{hash(str(sequence_number))[:8]}"
            
            qr_code_info = {
                "qr_data": qr_data,
                "sequence_number": sequence_number,
                "batch_id": batch_id
            }
            
            qr_codes.append(qr_code_info)
        
        logger.info(
            "Batch QR codes generated",
            batch_id=batch_id,
            quantity=quantity,
            start_sequence=start_sequence
        )
        
        return qr_codes
        
    except Exception as e:
        logger.error("Batch QR code generation failed", error=str(e))
        raise ValueError("Failed to generate batch QR codes")

def create_qr_code_image_with_border(
    qr_bytes: bytes,
    border_color: str = "black",
    border_width: int = 2
) -> bytes:
    """Add border to QR code image"""
    try:
        qr_image = Image.open(io.BytesIO(qr_bytes))
        
        # Create new image with border
        new_width = qr_image.width + (border_width * 2)
        new_height = qr_image.height + (border_width * 2)
        
        bordered_image = Image.new("RGB", (new_width, new_height), border_color)
        bordered_image.paste(qr_image, (border_width, border_width))
        
        # Convert to bytes
        output = io.BytesIO()
        bordered_image.save(output, format="PNG")
        bordered_bytes = output.getvalue()
        
        logger.info(
            "QR code border added",
            original_size=qr_image.size,
            new_size=bordered_image.size,
            border_width=border_width
        )
        
        return bordered_bytes
        
    except Exception as e:
        logger.error("QR code border addition failed", error=str(e))
        raise ValueError("Failed to add border to QR code")
