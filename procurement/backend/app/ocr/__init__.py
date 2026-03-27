"""OCR module — blob upload, text extraction, Azure Document Intelligence."""

from app.ocr.azure_blob import upload_to_blob
from app.ocr.azure_di import azure_di_ocr
from app.ocr.preocr_loader import load_preocr_text
from app.ocr.service import extract_text
from app.ocr.text_extract import extract_text_layer

__all__ = [
    "upload_to_blob",
    "azure_di_ocr",
    "load_preocr_text",
    "extract_text",
    "extract_text_layer",
]
