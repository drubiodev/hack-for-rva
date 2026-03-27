"""Field extractor using Azure OpenAI ChatGPT 5.4 mini — per-type prompts."""

import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)

_EXTRACTION_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "field_extraction",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": ["string", "null"], "description": "Document title or subject."},
                "document_number": {"type": ["string", "null"], "description": "Contract/PO/invoice number."},
                "vendor_name": {"type": ["string", "null"], "description": "Vendor or contractor name."},
                "issuing_department": {"type": ["string", "null"], "description": "City department issuing the document."},
                "total_amount": {"type": ["number", "null"], "description": "Total contract/invoice amount in dollars."},
                "currency": {"type": "string", "description": "Currency code (default USD)."},
                "document_date": {"type": ["string", "null"], "description": "Document date in YYYY-MM-DD format."},
                "effective_date": {"type": ["string", "null"], "description": "Contract effective/start date in YYYY-MM-DD."},
                "expiration_date": {"type": ["string", "null"], "description": "Contract expiration/end date in YYYY-MM-DD."},
                "contract_type": {"type": ["string", "null"], "description": "Type of contract (e.g., service, goods, construction)."},
                "payment_terms": {"type": ["string", "null"], "description": "Payment terms (e.g., Net 30)."},
                "renewal_clause": {"type": ["string", "null"], "description": "Renewal clause text if present."},
                "insurance_required": {"type": ["boolean", "null"], "description": "Whether insurance is required."},
                "bond_required": {"type": ["boolean", "null"], "description": "Whether a performance bond is required."},
                "scope_summary": {"type": ["string", "null"], "description": "Brief summary of scope of work (1-2 sentences)."},
                "extraction_confidence": {"type": "number", "description": "Overall extraction confidence 0.0-1.0."},
            },
            "required": [
                "title", "document_number", "vendor_name", "issuing_department",
                "total_amount", "currency", "document_date", "effective_date",
                "expiration_date", "contract_type", "payment_terms", "renewal_clause",
                "insurance_required", "bond_required", "scope_summary", "extraction_confidence",
            ],
            "additionalProperties": False,
        },
    },
}

_TYPE_HINTS: dict[str, str] = {
    "contract": "Focus on: parties, dollar amounts, effective/expiration dates, scope of work, insurance and bond requirements, renewal clauses.",
    "rfp": "Focus on: project title, issuing department, submission deadline (as document_date), estimated budget (as total_amount), scope of work.",
    "rfq": "Focus on: requested items/services, issuing department, response deadline (as document_date), estimated value.",
    "purchase_order": "Focus on: PO number, vendor, line-item total, delivery date (as effective_date), department.",
    "invoice": "Focus on: invoice number, vendor, total due, invoice date, payment terms.",
    "amendment": "Focus on: original contract number, amendment number, changed terms, new amounts or dates.",
    "cooperative": "Focus on: cooperative name, participating entities, contract terms, piggyback provisions.",
    "other": "Extract whatever fields are clearly present in the text.",
}

_SYSTEM_PROMPT = """You are a procurement data extractor for the City of Richmond, Virginia.
Given OCR-extracted text from a {doc_type} document, extract structured fields.

{type_hint}

Rules:
- OCR artifacts may be present — extract what is clearly legible
- Use YYYY-MM-DD format for all dates
- Return null for fields not found in the text
- Currency defaults to "USD" if not specified
- For total_amount, extract the primary contract/invoice value as a number (no $ sign)
- extraction_confidence should reflect how much of the text was clearly legible and extractable

AI-assisted extraction — requires human review."""


_EMPTY_RESULT: dict = {
    "title": None,
    "document_number": None,
    "vendor_name": None,
    "issuing_department": None,
    "total_amount": None,
    "currency": "USD",
    "document_date": None,
    "effective_date": None,
    "expiration_date": None,
    "contract_type": None,
    "payment_terms": None,
    "renewal_clause": None,
    "insurance_required": None,
    "bond_required": None,
    "scope_summary": None,
    "extraction_confidence": 0.0,
}


async def extract_fields(ocr_text: str, document_type: str) -> dict:
    """Extract structured fields from OCR text using ChatGPT 5.4 mini.

    Returns dict matching ExtractedFields columns.
    """
    if "PLACEHOLDER" in settings.azure_openai_key:
        logger.warning("Azure OpenAI credentials are PLACEHOLDER — returning empty extraction")
        return dict(_EMPTY_RESULT)

    if not ocr_text.strip():
        return dict(_EMPTY_RESULT)

    from openai import AsyncAzureOpenAI

    client = AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_key,
        api_version=settings.azure_openai_api_version,
    )

    type_hint = _TYPE_HINTS.get(document_type, _TYPE_HINTS["other"])
    system = _SYSTEM_PROMPT.format(doc_type=document_type, type_hint=type_hint)

    # Use more text for extraction than classification
    truncated = ocr_text[:8000]

    try:
        response = await client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"Extract fields from this {document_type}:\n\n{truncated}"},
            ],
            response_format=_EXTRACTION_SCHEMA,
            temperature=0.0,
            max_tokens=800,
        )

        result = json.loads(response.choices[0].message.content)

        # Ensure all expected keys are present
        for key in _EMPTY_RESULT:
            if key not in result:
                result[key] = _EMPTY_RESULT[key]

        logger.info(
            "Extracted fields: vendor=%s, amount=%s, confidence=%.2f",
            result.get("vendor_name"),
            result.get("total_amount"),
            result.get("extraction_confidence", 0.0),
        )
        return result

    except Exception:
        logger.exception("Field extraction failed")
        return dict(_EMPTY_RESULT)
