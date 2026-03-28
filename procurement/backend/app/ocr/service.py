"""OCR service — orchestrates text extraction with fallbacks."""

import logging

from app.config import settings
from app.ocr.azure_di import azure_di_ocr
from app.ocr.preocr_loader import load_preocr_text
from app.ocr.text_extract import extract_text_layer

logger = logging.getLogger(__name__)

_IMAGE_MIMES = {"image/png", "image/jpeg", "image/jpg", "image/tiff"}


async def extract_text(
    file_path: str,
    blob_url: str,
    mime_type: str,
    original_filename: str | None = None,
) -> tuple[str, float]:
    """Try text layer first (free, instant), fall back to Azure DI. Returns (text, confidence).

    In dev mode (PLACEHOLDER credentials), tries pre-OCR'd text first.
    """
    is_dev = "PLACEHOLDER" in settings.azure_di_key

    # 1. In dev mode, try pre-OCR'd text first
    if is_dev and original_filename:
        preocr = load_preocr_text(original_filename)
        if preocr:
            logger.info("Using pre-OCR'd text for %s", original_filename)
            return (preocr, 0.95)

    # 2. For PDFs, try embedded text layer (free, instant)
    if mime_type == "application/pdf":
        text = extract_text_layer(file_path)
        if text:
            return (text, 0.99)  # Embedded text is high confidence

    # 3. For images or scanned PDFs, use Azure DI
    if mime_type in _IMAGE_MIMES or mime_type == "application/pdf":
        text, confidence = await azure_di_ocr(blob_url, file_path=file_path)
        if text:
            return (text, confidence)

    logger.warning("No text extracted from %s (mime=%s)", file_path, mime_type)
    return ("", 0.0)
