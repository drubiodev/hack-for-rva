"""Extraction module — document classification + field extraction."""

from app.extraction.classifier import classify_document
from app.extraction.extractor import extract_fields

__all__ = ["classify_document", "extract_fields"]
