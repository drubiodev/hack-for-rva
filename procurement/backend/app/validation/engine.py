"""Validation engine — 13 rule-based checks + AI consistency."""

import json
import logging
from datetime import date, timedelta

from app.config import settings

logger = logging.getLogger(__name__)


def _result(rule_code: str, severity: str, message: str, field_name: str | None = None, suggestion: str | None = None) -> dict:
    return {
        "rule_code": rule_code,
        "severity": severity,
        "field_name": field_name,
        "message": message,
        "suggestion": suggestion,
    }


def _parse_date(val: str | date | None) -> date | None:
    if val is None:
        return None
    if isinstance(val, date):
        return val
    try:
        return date.fromisoformat(val)
    except (ValueError, TypeError):
        return None


def _run_rule_checks(fields: dict, ocr_confidence: float, classification_confidence: float) -> list[dict]:
    """Run 13 rule-based validation checks."""
    results: list[dict] = []
    doc_type = fields.get("contract_type") or fields.get("_document_type") or ""
    amount = fields.get("total_amount")
    vendor = fields.get("vendor_name")
    expiration = _parse_date(fields.get("expiration_date"))
    effective = _parse_date(fields.get("effective_date"))
    doc_date = _parse_date(fields.get("document_date"))
    insurance = fields.get("insurance_required")
    bond = fields.get("bond_required")
    today = date.today()

    # Determine if this is a contract-type doc (uses _document_type from pipeline)
    is_contract_type = fields.get("_document_type", "") in ("contract", "purchase_order", "amendment", "cooperative")

    # 1. MISSING_AMOUNT
    if amount is None and is_contract_type:
        results.append(_result(
            "MISSING_AMOUNT", "warning",
            "No total amount found on this document.",
            "total_amount",
            "Verify the contract value and enter it manually.",
        ))

    # 2. DATE_LOGIC
    if effective and expiration and expiration < effective:
        results.append(_result(
            "DATE_LOGIC", "error",
            f"Expiration date ({expiration}) is before effective date ({effective}).",
            "expiration_date",
            "Check if dates were extracted correctly — possible OCR error.",
        ))

    # 3. CONTRACT_EXPIRING_30
    if expiration and 0 < (expiration - today).days <= 30:
        results.append(_result(
            "CONTRACT_EXPIRING_30", "error",
            f"Contract expires within 30 days ({expiration}).",
            "expiration_date",
            "Initiate renewal process or notify procurement.",
        ))

    # 4. CONTRACT_EXPIRING_90
    if expiration and 30 < (expiration - today).days <= 90:
        results.append(_result(
            "CONTRACT_EXPIRING_90", "warning",
            f"Contract expires within 90 days ({expiration}).",
            "expiration_date",
            "Plan for upcoming renewal or re-procurement.",
        ))

    # 5. CONTRACT_EXPIRED
    if expiration and expiration < today:
        results.append(_result(
            "CONTRACT_EXPIRED", "error",
            f"Contract expired on {expiration}.",
            "expiration_date",
            "Review whether services are still being received under an expired contract.",
        ))

    # 6. HIGH_VALUE_NO_BOND
    if amount and amount > 100_000 and is_contract_type and bond is not True:
        results.append(_result(
            "HIGH_VALUE_NO_BOND", "warning",
            f"Contract value ${amount:,.2f} exceeds $100K but no bond requirement found.",
            "bond_required",
            "Verify whether a performance bond should be required.",
        ))

    # 7. AMOUNT_RANGE
    if amount and amount > 10_000_000:
        results.append(_result(
            "AMOUNT_RANGE", "warning",
            f"Amount ${amount:,.2f} exceeds $10M — may be an OCR extraction error.",
            "total_amount",
            "Verify the extracted amount against the original document.",
        ))

    # 8. LOW_OCR_CONFIDENCE
    if ocr_confidence < 0.85 and ocr_confidence > 0.0:
        results.append(_result(
            "LOW_OCR_CONFIDENCE", "warning",
            f"OCR confidence is {ocr_confidence:.1%} (below 85% threshold).",
            None,
            "Consider re-scanning the document at higher resolution.",
        ))

    # 9. LOW_CLASSIFICATION
    if classification_confidence < 0.75 and classification_confidence > 0.0:
        results.append(_result(
            "LOW_CLASSIFICATION", "warning",
            f"Document classification confidence is {classification_confidence:.1%}.",
            None,
            "Verify the document type is correct.",
        ))

    # 10. MISSING_VENDOR
    if not vendor:
        results.append(_result(
            "MISSING_VENDOR", "warning",
            "No vendor name found in the document.",
            "vendor_name",
            "Enter the vendor name manually.",
        ))

    # 11. MISSING_EXPIRATION — elevated to error for contract types
    if not expiration and is_contract_type:
        source = fields.get("expiration_date_source") or ""
        msg = "No expiration date found on this contract/PO."
        if source:
            msg += f" AI note: {source}"
        results.append(_result(
            "MISSING_EXPIRATION", "error",
            msg,
            "expiration_date",
            "Enter the expiration date manually — this is critical for renewal tracking.",
        ))

    # 11b. LOW_EXPIRATION_CONFIDENCE — field-level confidence below threshold
    field_confs = fields.get("field_confidences", {})
    exp_conf = field_confs.get("expiration_date")
    threshold = settings.confidence_threshold
    if expiration and exp_conf is not None and exp_conf < threshold:
        results.append(_result(
            "LOW_EXPIRATION_CONFIDENCE", "warning",
            f"Expiration date confidence is {exp_conf:.0%} (below {threshold:.0%} threshold). "
            f"The extracted date {expiration} may be incorrect.",
            "expiration_date",
            "Verify the expiration date against the original document before relying on it for renewal decisions.",
        ))

    # 11c. LOW_FIELD_CONFIDENCE — flag any other fields below threshold
    _CRITICAL_FIELDS = {"vendor_name", "total_amount", "effective_date"}
    for fname in _CRITICAL_FIELDS:
        fconf = field_confs.get(fname)
        if fconf is not None and fconf < threshold and fields.get(fname) is not None:
            results.append(_result(
                "LOW_FIELD_CONFIDENCE", "warning",
                f"{fname.replace('_', ' ').title()} confidence is {fconf:.0%} (below {threshold:.0%} threshold).",
                fname,
                f"Verify {fname.replace('_', ' ')} against the original document.",
            ))

    # 14. DATE_RANGE — catch AI hallucinated dates
    for field_name, field_date in [
        ("document_date", doc_date),
        ("effective_date", effective),
        ("expiration_date", expiration),
    ]:
        if field_date and (field_date.year < 2000 or field_date.year > 2035):
            results.append(_result(
                "DATE_RANGE", "warning",
                f"{field_name.replace('_', ' ').title()} ({field_date}) seems unlikely — year {field_date.year} is outside expected range (2000-2035).",
                field_name,
                "Verify this date against the original document — may be an AI extraction error.",
            ))

    # S16. COMPLIANCE_MISSING — MBE/WBE warning for high-value contracts
    mbe_wbe = fields.get("mbe_wbe_required")
    if amount and amount > 100_000 and is_contract_type and mbe_wbe is not True:
        results.append(_result(
            "COMPLIANCE_MISSING", "warning",
            f"Contract value ${amount:,.2f} exceeds $100K but no MBE/WBE requirement found.",
            "mbe_wbe_required",
            "Verify whether MBE/WBE participation should be required per City policy.",
        ))

    # S17. BOND_AMOUNT_MISMATCH — construction contracts where bond != total amount
    perf_bond = fields.get("performance_bond_amount")
    contract_type_lower = (doc_type or "").lower()
    if (
        is_contract_type
        and "construction" in contract_type_lower
        and perf_bond is not None
        and amount is not None
        and perf_bond != amount
    ):
        results.append(_result(
            "BOND_AMOUNT_MISMATCH", "warning",
            f"Performance bond ${perf_bond:,.2f} does not match contract amount ${amount:,.2f}.",
            "performance_bond_amount",
            "For construction contracts, the performance bond typically equals the total contract amount.",
        ))

    # 12. MISSING_INSURANCE
    if amount and amount > 50_000 and is_contract_type and insurance is not True:
        results.append(_result(
            "MISSING_INSURANCE", "info",
            f"Contract value ${amount:,.2f} exceeds $50K but no insurance requirement found.",
            "insurance_required",
            "Verify whether liability insurance should be required.",
        ))

    # 13. MISSING_DATE
    if not doc_date:
        results.append(_result(
            "MISSING_DATE", "warning",
            "No document date found.",
            "document_date",
            "Enter the document date manually.",
        ))

    return results


async def _ai_consistency_check(fields: dict) -> list[dict]:
    """Optional AI consistency check using ChatGPT 5.4 mini."""
    if "PLACEHOLDER" in settings.azure_openai_key:
        return []

    import httpx
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        base_url=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_key,
        timeout=httpx.Timeout(30.0),
    )

    # Remove internal keys for prompt
    clean_fields = {k: v for k, v in fields.items() if not k.startswith("_")}

    schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "consistency_check",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field_name": {"type": "string"},
                                "message": {"type": "string"},
                                "suggestion": {"type": "string"},
                            },
                            "required": ["field_name", "message", "suggestion"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["issues"],
                "additionalProperties": False,
            },
        },
    }

    try:
        response = await client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a procurement data quality checker. "
                        "Review extracted fields for cross-field consistency issues. "
                        "Only flag clear logical inconsistencies (e.g., vendor name in department field, "
                        "payment terms that don't match amount, scope that contradicts contract type). "
                        "Return an empty issues array if everything looks consistent."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Check these extracted fields for consistency:\n{json.dumps(clean_fields, indent=2, default=str)}",
                },
            ],
            response_format=schema,
            temperature=0.0,
            max_completion_tokens=400,
        )

        result = json.loads(response.choices[0].message.content)
        return [
            _result(
                "AI_CONSISTENCY",
                "warning",
                issue["message"],
                issue["field_name"],
                issue["suggestion"],
            )
            for issue in result.get("issues", [])
        ]

    except Exception:
        logger.exception("AI consistency check failed")
        return []


async def validate_document(
    extracted_fields: dict,
    ocr_confidence: float,
    classification_confidence: float,
) -> list[dict]:
    """Run 13 rule-based checks + AI consistency. Returns list of validation result dicts."""
    results = _run_rule_checks(extracted_fields, ocr_confidence, classification_confidence)
    ai_results = await _ai_consistency_check(extracted_fields)
    results.extend(ai_results)

    logger.info(
        "Validation complete: %d issues (%d errors, %d warnings, %d info)",
        len(results),
        sum(1 for r in results if r["severity"] == "error"),
        sum(1 for r in results if r["severity"] == "warning"),
        sum(1 for r in results if r["severity"] == "info"),
    )
    return results
