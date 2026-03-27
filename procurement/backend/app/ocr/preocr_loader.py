"""Load pre-OCR'd text files for development without Azure credentials."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Pre-OCR'd text lives relative to the project root
_PREOCR_DIR = Path(__file__).resolve().parents[4] / "pillar-thriving-city-hall" / "procurement-examples" / "txt"


def load_preocr_text(original_filename: str) -> str | None:
    """Load pre-OCR'd text from pillar-thriving-city-hall/procurement-examples/txt/.

    Matches by stem: "Contract 24000006048.pdf" -> "Contract 24000006048.txt"
    """
    if not original_filename:
        return None

    stem = Path(original_filename).stem
    txt_path = _PREOCR_DIR / f"{stem}.txt"

    if txt_path.exists():
        text = txt_path.read_text(encoding="utf-8").strip()
        logger.info("Loaded pre-OCR'd text for %s (%d chars)", original_filename, len(text))
        return text

    # Also try case-insensitive match
    if _PREOCR_DIR.exists():
        for f in _PREOCR_DIR.iterdir():
            if f.stem.lower() == stem.lower() and f.suffix == ".txt":
                text = f.read_text(encoding="utf-8").strip()
                logger.info("Loaded pre-OCR'd text for %s (%d chars, case-insensitive)", original_filename, len(text))
                return text

    logger.debug("No pre-OCR'd text found for %s", original_filename)
    return None
