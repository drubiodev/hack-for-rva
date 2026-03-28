"""Document classifier using Azure OpenAI ChatGPT 5.4 mini."""

import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)

VALID_TYPES = {"rfp", "rfq", "contract", "purchase_order", "invoice", "amendment", "cooperative", "other"}

_CLASSIFY_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "document_classification",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "document_type": {
                    "type": "string",
                    "enum": list(VALID_TYPES),
                    "description": "The classified document type.",
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence score between 0.0 and 1.0.",
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation of why this type was chosen.",
                },
            },
            "required": ["document_type", "confidence", "reasoning"],
            "additionalProperties": False,
        },
    },
}

_SYSTEM_PROMPT = """You are a procurement document classifier for the City of Richmond, Virginia.
Given OCR-extracted text from a document, classify it into exactly one type.

Document types:
- rfp: Request for Proposal
- rfq: Request for Quotation
- contract: Signed contract or agreement
- purchase_order: Purchase order
- invoice: Invoice or billing document
- amendment: Contract amendment or modification
- cooperative: Cooperative procurement agreement
- other: Does not fit any category

Return your classification with a confidence score (0.0-1.0).
OCR artifacts may be present — classify based on overall content."""


async def classify_document(ocr_text: str) -> tuple[str, float]:
    """Classify document type using ChatGPT 5.4 mini. Returns (document_type, confidence)."""
    if "PLACEHOLDER" in settings.azure_openai_key:
        logger.warning("Azure OpenAI credentials are PLACEHOLDER — returning default classification")
        return ("other", 0.0)

    if not ocr_text.strip():
        return ("other", 0.0)

    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        base_url=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_key,
    )

    # Truncate to avoid token limits (first 4000 chars is enough for classification)
    truncated = ocr_text[:4000]

    try:
        response = await client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"Classify this document:\n\n{truncated}"},
            ],
            response_format=_CLASSIFY_SCHEMA,
            temperature=0.0,
            max_completion_tokens=200,
        )

        result = json.loads(response.choices[0].message.content)
        doc_type = result["document_type"]
        confidence = float(result["confidence"])

        if doc_type not in VALID_TYPES:
            doc_type = "other"

        logger.info("Classified as %s (confidence=%.2f)", doc_type, confidence)
        return (doc_type, confidence)

    except Exception:
        logger.exception("Classification failed")
        return ("other", 0.0)
