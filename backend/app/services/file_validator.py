"""Defense-in-depth file validation pipeline."""

import io
import os
import logging
from pathlib import Path
from typing import Dict

from fastapi import UploadFile, HTTPException, status

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logging.warning("python-magic not available - magic number validation disabled")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("Pillow not available - image verification disabled")

from app.config import Settings


async def validate_file_upload(file: UploadFile, settings: Settings) -> Dict[str, any]:
    """
    Validate uploaded file using defense-in-depth approach.

    Validation layers:
    1. Extension whitelist
    2. Filename sanitization (path traversal check)
    3. File size limit
    4. Magic number validation (MIME type)
    5. Image verification (for image files)

    Args:
        file: Uploaded file to validate
        settings: Application settings

    Returns:
        Dict with validated metadata: safe_filename, mime_type, size, extension

    Raises:
        HTTPException: If validation fails at any layer
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bestandsnaam ontbreekt"
        )

    # Layer 1: Extension whitelist
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bestandstype '{ext}' is niet toegestaan. Toegestaan: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Layer 2: Filename sanitization (path traversal check)
    safe_filename = os.path.basename(file.filename)
    if safe_filename != file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ongeldige bestandsnaam (padtraversal gedetecteerd)"
        )

    # Layer 3: File size limit
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Bestand overschrijdt de maximale grootte van {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB"
        )

    # Layer 4: Magic number validation
    mime_type = None
    if MAGIC_AVAILABLE:
        try:
            mime_type = magic.from_buffer(content, mime=True)
            if mime_type not in settings.ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Bestandsinhoud '{mime_type}' komt niet overeen met extensie '{ext}'"
                )
        except Exception as e:
            logging.warning(f"Magic number validation failed: {e}")
            # Fall back to extension-based MIME type
            mime_type = _get_mime_from_extension(ext)
    else:
        # Fall back to extension-based MIME type
        mime_type = _get_mime_from_extension(ext)

    # Layer 5: Image verification (for image files)
    if PIL_AVAILABLE and mime_type and mime_type.startswith('image/'):
        try:
            img = Image.open(io.BytesIO(content))
            img.verify()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ongeldig of beschadigd afbeeldingsbestand"
            )

    # Reset file position for later reading
    await file.seek(0)

    return {
        'safe_filename': safe_filename,
        'mime_type': mime_type,
        'size': len(content),
        'extension': ext
    }


def _get_mime_from_extension(ext: str) -> str:
    """Get MIME type from file extension (fallback)."""
    mime_map = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc': 'application/msword',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.tiff': 'image/tiff',
        '.bmp': 'image/bmp',
    }
    return mime_map.get(ext.lower(), 'application/octet-stream')
