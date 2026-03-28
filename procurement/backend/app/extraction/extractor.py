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
                "expiration_date": {"type": ["string", "null"], "description": "Contract expiration/end date in YYYY-MM-DD. THIS IS THE MOST CRITICAL FIELD — search the entire document for termination dates, end dates, expiry dates, or renewal deadlines. If the contract piggybacks on another contract, extract that contract's expiration if available."},
                "expiration_date_source": {"type": ["string", "null"], "description": "Exact quote from the document text where you found the expiration date, or explanation of why no date was found (e.g., 'tied to parent contract expiration', 'no explicit end date found')."},
                "contract_type": {"type": ["string", "null"], "description": "Type of contract (e.g., service, goods, construction)."},
                "payment_terms": {"type": ["string", "null"], "description": "Payment terms (e.g., Net 30)."},
                "renewal_clause": {"type": ["string", "null"], "description": "Renewal clause text if present."},
                "insurance_required": {"type": ["boolean", "null"], "description": "Whether insurance is required."},
                "bond_required": {"type": ["boolean", "null"], "description": "Whether a performance bond is required."},
                "scope_summary": {"type": ["string", "null"], "description": "Brief summary of scope of work (1-2 sentences)."},
                "extraction_confidence": {"type": "number", "description": "Overall extraction confidence 0.0-1.0."},
                "field_confidences": {
                    "type": "object",
                    "description": "Per-field confidence scores (0.0-1.0). Score 1.0 = found explicit text. Score 0.5-0.9 = inferred/partial. Score 0.0 = not found. Be especially precise for expiration_date.",
                    "properties": {
                        "title": {"type": "number"},
                        "vendor_name": {"type": "number"},
                        "total_amount": {"type": "number"},
                        "effective_date": {"type": "number"},
                        "expiration_date": {"type": "number"},
                        "contract_type": {"type": "number"},
                        "payment_terms": {"type": "number"},
                        "insurance_required": {"type": "number"},
                        "bond_required": {"type": "number"},
                    },
                    "required": ["title", "vendor_name", "total_amount", "effective_date", "expiration_date", "contract_type", "payment_terms", "insurance_required", "bond_required"],
                    "additionalProperties": False,
                },
            },
            "required": [
                "title", "document_number", "vendor_name", "issuing_department",
                "total_amount", "currency", "document_date", "effective_date",
                "expiration_date", "expiration_date_source", "contract_type", "payment_terms", "renewal_clause",
                "insurance_required", "bond_required", "scope_summary", "extraction_confidence",
                "field_confidences",
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

CRITICAL — EXPIRATION DATE:
The expiration_date is the MOST IMPORTANT field for procurement risk management. Search thoroughly:
- Look for "expiration", "termination", "end date", "expires", "shall expire", "term ends"
- If the contract piggybacks on another contract (e.g., cooperative/state contract), note the parent contract's expiration
- If the contract says "X years from effective date", calculate the expiration date
- If there is a renewal clause with specific dates, extract the final possible expiration
- Set expiration_date_source to the exact text you found, or explain why no date was found

FIELD CONFIDENCES:
For each field in field_confidences, score 0.0-1.0:
- 1.0 = found explicit, unambiguous text in the document
- 0.7-0.9 = found but partially obscured, inferred from context, or OCR may have errors
- 0.3-0.6 = weak inference or uncertain extraction
- 0.0 = field not found at all (return null for the field value)

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
    "expiration_date_source": None,
    "contract_type": None,
    "payment_terms": None,
    "renewal_clause": None,
    "insurance_required": None,
    "bond_required": None,
    "scope_summary": None,
    "extraction_confidence": 0.0,
    "field_confidences": {},
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

    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        base_url=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_key,
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
            max_completion_tokens=1200,
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
