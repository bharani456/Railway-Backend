"""
Image processing utilities
"""

import io
from PIL import Image, ImageOps
from typing import List, Tuple, Optional
import base64
import structlog

from app.config.settings import get_settings

logger = structlog.get_logger()
settings = get_settings()

def compress_image(image_data: bytes, quality: int = None) -> bytes:
    """Compress image while maintaining quality"""
    if quality is None:
        quality = settings.IMAGE_COMPRESSION_QUALITY
    
    try:
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Compress image
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=quality, optimize=True)
        compressed_data = output.getvalue()
        
        logger.info(
            "Image compressed",
            original_size=len(image_data),
            compressed_size=len(compressed_data),
            compression_ratio=len(compressed_data) / len(image_data)
        )
        
        return compressed_data
        
    except Exception as e:
        logger.error("Image compression failed", error=str(e))
        raise ValueError("Failed to compress image")

def create_thumbnail(image_data: bytes, size: Tuple[int, int] = None) -> bytes:
    """Create thumbnail from image"""
    if size is None:
        size = settings.THUMBNAIL_SIZE
    
    try:
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Create thumbnail
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Save thumbnail
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=85, optimize=True)
        thumbnail_data = output.getvalue()
        
        logger.info(
            "Thumbnail created",
            original_size=len(image_data),
            thumbnail_size=len(thumbnail_data),
            thumbnail_dimensions=image.size
        )
        
        return thumbnail_data
        
    except Exception as e:
        logger.error("Thumbnail creation failed", error=str(e))
        raise ValueError("Failed to create thumbnail")

def validate_image(image_data: bytes) -> bool:
    """Validate image format and size"""
    try:
        # Check file size
        if len(image_data) > settings.MAX_UPLOAD_SIZE:
            return False
        
        # Try to open image
        image = Image.open(io.BytesIO(image_data))
        
        # Check format
        if image.format not in ["JPEG", "PNG", "WEBP"]:
            return False
        
        # Check dimensions (minimum 100x100, maximum 5000x5000)
        width, height = image.size
        if width < 100 or height < 100 or width > 5000 or height > 5000:
            return False
        
        return True
        
    except Exception as e:
        logger.error("Image validation failed", error=str(e))
        return False

def base64_to_image(base64_string: str) -> bytes:
    """Convert base64 string to image bytes"""
    try:
        # Remove data URL prefix if present
        if base64_string.startswith("data:image/"):
            base64_string = base64_string.split(",")[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Validate image
        if not validate_image(image_data):
            raise ValueError("Invalid image format or size")
        
        return image_data
        
    except Exception as e:
        logger.error("Base64 to image conversion failed", error=str(e))
        raise ValueError("Failed to convert base64 to image")

def image_to_base64(image_data: bytes) -> str:
    """Convert image bytes to base64 string"""
    try:
        base64_string = base64.b64encode(image_data).decode("utf-8")
        return f"data:image/jpeg;base64,{base64_string}"
    except Exception as e:
        logger.error("Image to base64 conversion failed", error=str(e))
        raise ValueError("Failed to convert image to base64")

def extract_image_metadata(image_data: bytes) -> dict:
    """Extract metadata from image"""
    try:
        image = Image.open(io.BytesIO(image_data))
        
        metadata = {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "width": image.size[0],
            "height": image.size[1],
            "file_size": len(image_data)
        }
        
        # Extract EXIF data if available
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            metadata["exif"] = exif
        
        return metadata
        
    except Exception as e:
        logger.error("Metadata extraction failed", error=str(e))
        return {}

def resize_image(image_data: bytes, max_width: int, max_height: int) -> bytes:
    """Resize image to fit within specified dimensions"""
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Calculate new size maintaining aspect ratio
        width, height = image.size
        ratio = min(max_width / width, max_height / height)
        
        if ratio < 1:
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save resized image
        output = io.BytesIO()
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        image.save(output, format="JPEG", quality=85, optimize=True)
        resized_data = output.getvalue()
        
        logger.info(
            "Image resized",
            original_size=image.size,
            new_size=image.size,
            file_size=len(resized_data)
        )
        
        return resized_data
        
    except Exception as e:
        logger.error("Image resize failed", error=str(e))
        raise ValueError("Failed to resize image")
