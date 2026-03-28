"""Field extractor using Azure OpenAI ChatGPT 5.4 mini — per-type prompts."""

import json
import logging
import re

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

_HIGH_VALUE_KEYWORDS = [
    "expir", "terminat", "end date", "renew", "insurance", "bond",
    "performance bond", "indemnif", "total amount", "not to exceed",
    "effective date", "commence", "shall expire",
]

_CHARS_PER_PAGE = 3000


def _smart_truncate(text: str, budget: int = 8000) -> str:
    """Strategically truncate OCR text to fit within token budget.

    Instead of naively slicing the first N chars, scans the full document
    for high-value keyword windows (expiration dates, amounts, insurance, etc.)
    and assembles a representative sample.
    """
    if len(text) <= budget:
        return text

    head_budget = 2500
    tail_budget = 1500
    keyword_budget = budget - head_budget - tail_budget - 100  # markers overhead

    # Find 500-char windows around high-value keywords
    window_half = 250
    text_lower = text.lower()
    windows: list[tuple[int, int]] = []

    for kw in _HIGH_VALUE_KEYWORDS:
        start = 0
        while True:
            idx = text_lower.find(kw, start)
            if idx == -1:
                break
            win_start = max(0, idx - window_half)
            win_end = min(len(text), idx + window_half)
            windows.append((win_start, win_end))
            start = idx + len(kw)

    if not windows:
        # Fallback: first 6500 + last 1500
        return text[:budget - tail_budget] + "\n\n[...document continues...]\n\n" + text[-tail_budget:]

    # Sort by position and deduplicate overlapping windows
    windows.sort()
    merged: list[tuple[int, int]] = []
    for ws, we in windows:
        if merged and ws <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], we))
        else:
            merged.append((ws, we))

    # Skip windows that overlap with head or tail
    head_end = head_budget
    tail_start = len(text) - tail_budget
    filtered = [(s, e) for s, e in merged if s >= head_end and e <= tail_start]

    # Collect keyword windows within budget
    keyword_parts: list[str] = []
    used = 0
    for ws, we in filtered:
        chunk = text[ws:we]
        if used + len(chunk) > keyword_budget:
            break
        page_num = ws // _CHARS_PER_PAGE + 1
        keyword_parts.append(f"[...page ~{page_num}...]\n{chunk}")
        used += len(chunk)

    # Assemble
    parts = [text[:head_budget]]
    if keyword_parts:
        parts.append("\n\n[...document continues...]\n\n")
        parts.append("\n\n".join(keyword_parts))
    parts.append("\n\n[...document continues...]\n\n")
    parts.append(text[-tail_budget:])

    return "".join(parts)


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
- The text may contain [...document continues...] and [...page ~N...] gap markers indicating
  skipped sections. Extract fields from ALL available sections, not just the beginning.
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

    import httpx
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        base_url=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_key,
        timeout=httpx.Timeout(30.0),
    )

    type_hint = _TYPE_HINTS.get(document_type, _TYPE_HINTS["other"])
    system = _SYSTEM_PROMPT.format(doc_type=document_type, type_hint=type_hint)

    # Smart truncation: capture keyword-rich sections across the full document
    truncated = _smart_truncate(ocr_text)

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
