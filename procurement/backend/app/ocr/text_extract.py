"""Extract embedded text layer from PDFs (free, instant — no OCR needed)."""

import logging

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 100


def extract_text_layer(file_path: str) -> str | None:
    """Try to extract embedded text from PDF. Returns None if scanned/image."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        pages_text: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        full_text = "\n".join(pages_text).strip()
        if len(full_text) < MIN_TEXT_LENGTH:
            logger.info("PDF text layer too short (%d chars) — likely scanned", len(full_text))
            return None

        logger.info("Extracted %d chars from PDF text layer", len(full_text))
        return full_text
    except Exception:
        logger.exception("Failed to extract text layer from %s", file_path)
        return None
