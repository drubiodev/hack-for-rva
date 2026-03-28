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


def _evaluate_deterministic_rules(fields: dict, rules: list) -> list[dict]:
    """Evaluate deterministic custom policy rules against extracted fields."""
    from app.validation.districts import RICHMOND_DISTRICTS, RICHMOND_NEIGHBORHOODS

    results: list[dict] = []
    doc_type = fields.get("_document_type", "")

    for rule in rules:
        # Access attributes (works for both ORM objects and dicts)
        r_type = getattr(rule, "rule_type", None) or (rule.get("rule_type") if isinstance(rule, dict) else None)

        # Skip semantic_policy rules — handled separately
        if r_type == "semantic_policy":
            continue

        r_scope = getattr(rule, "scope", "global") if not isinstance(rule, dict) else rule.get("scope", "global")
        r_dept = getattr(rule, "department", None) if not isinstance(rule, dict) else rule.get("department")
        r_doc_types = getattr(rule, "applies_to_doc_types", None) if not isinstance(rule, dict) else rule.get("applies_to_doc_types")
        r_field = getattr(rule, "field_name", None) if not isinstance(rule, dict) else rule.get("field_name")
        r_operator = getattr(rule, "operator", None) if not isinstance(rule, dict) else rule.get("operator")
        r_threshold = getattr(rule, "threshold_value", None) if not isinstance(rule, dict) else rule.get("threshold_value")
        r_name = getattr(rule, "name", "unknown") if not isinstance(rule, dict) else rule.get("name", "unknown")
        r_severity = getattr(rule, "severity", "warning") if not isinstance(rule, dict) else rule.get("severity", "warning")
        r_msg = getattr(rule, "message_template", None) if not isinstance(rule, dict) else rule.get("message_template")
        r_suggestion = getattr(rule, "suggestion", None) if not isinstance(rule, dict) else rule.get("suggestion")
        r_id = getattr(rule, "id", None) if not isinstance(rule, dict) else rule.get("id")

        # Scope check: department-scoped rules only apply to matching departments
        if r_scope == "department" and r_dept:
            primary_dept = fields.get("primary_department", "")
            dept_tags = fields.get("department_tags", []) or []
            dept_match = (
                (primary_dept and r_dept.lower() in primary_dept.lower())
                or any(r_dept.lower() in t.lower() for t in dept_tags)
            )
            if not dept_match:
                continue

        # Document type check
        if r_doc_types and doc_type and doc_type not in r_doc_types:
            continue

        triggered = False
        field_value = fields.get(r_field) if r_field else None

        if r_type == "threshold" and r_field:
            try:
                val = float(field_value) if field_value is not None else None
                thresh = float(r_threshold) if r_threshold is not None else None
                if val is not None and thresh is not None:
                    ops = {
                        "gt": val > thresh,
                        "lt": val < thresh,
                        "gte": val >= thresh,
                        "lte": val <= thresh,
                        "eq": val == thresh,
                        "neq": val != thresh,
                    }
                    triggered = ops.get(r_operator, False)
            except (ValueError, TypeError):
                pass

        elif r_type == "required_field" and r_field:
            if r_operator == "is_empty":
                triggered = field_value is None or field_value == "" or field_value == []
            elif r_operator == "is_not_empty":
                triggered = bool(field_value)
            else:
                # Default: check field is present and truthy
                triggered = not bool(field_value)

        elif r_type == "district_check":
            # Check if scope_summary or OCR text mentions Richmond districts/neighborhoods
            text_to_check = (fields.get("scope_summary") or "").lower()
            all_locations = RICHMOND_DISTRICTS + RICHMOND_NEIGHBORHOODS
            found = [loc for loc in all_locations if loc.lower() in text_to_check]
            triggered = len(found) == 0  # Trigger if NO district/neighborhood found

        elif r_type == "date_window" and r_field:
            field_date = _parse_date(field_value)
            if field_date and r_threshold:
                try:
                    days = int(float(r_threshold))
                    today = date.today()
                    triggered = abs((field_date - today).days) <= days
                except (ValueError, TypeError):
                    pass

        if triggered:
            # Template substitution
            message = r_msg or f"Policy rule '{r_name}' triggered."
            message = message.replace("{field}", str(r_field or ""))
            message = message.replace("{value}", str(field_value or ""))
            message = message.replace("{threshold}", str(r_threshold or ""))

            result = _result(
                rule_code=f"POLICY:{r_name}",
                severity=r_severity,
                field_name=r_field,
                message=message,
                suggestion=r_suggestion,
            )
            result["policy_rule_id"] = r_id
            results.append(result)

    return results


async def _evaluate_semantic_policies(fields: dict, ocr_text: str, rules: list) -> list[dict]:
    """Evaluate semantic policy rules using AI."""
    from app.extraction.extractor import _smart_truncate

    # Filter to semantic_policy rules only
    semantic_rules = []
    for rule in rules:
        r_type = getattr(rule, "rule_type", None) or (rule.get("rule_type") if isinstance(rule, dict) else None)
        if r_type == "semantic_policy":
            semantic_rules.append(rule)

    if not semantic_rules:
        return []

    if "PLACEHOLDER" in settings.azure_openai_key:
        return []

    import httpx
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        base_url=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_key,
        timeout=httpx.Timeout(30.0),
    )

    all_results: list[dict] = []

    # Batch into groups of 10
    batch_size = 10
    for batch_start in range(0, len(semantic_rules), batch_size):
        batch = semantic_rules[batch_start:batch_start + batch_size]

        # Build numbered rule list
        rule_lines = []
        for i, rule in enumerate(batch, 1):
            r_name = getattr(rule, "name", "") if not isinstance(rule, dict) else rule.get("name", "")
            r_policy = getattr(rule, "policy_statement", "") if not isinstance(rule, dict) else rule.get("policy_statement", "")
            rule_lines.append(f"{i}. [{r_name}]: {r_policy}")

        rules_text = "\n".join(rule_lines)

        # Build document data
        clean_fields = {k: v for k, v in fields.items() if not k.startswith("_")}
        truncated_ocr = _smart_truncate(ocr_text, budget=4000) if ocr_text else ""

        schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "semantic_policy_eval",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "evaluations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "rule_number": {"type": "integer"},
                                    "verdict": {"type": "string", "enum": ["COMPLIANT", "VIOLATES", "INSUFFICIENT_DATA"]},
                                    "evidence": {"type": "string"},
                                    "confidence": {"type": "number"},
                                },
                                "required": ["rule_number", "verdict", "evidence", "confidence"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["evaluations"],
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
                            "You are a procurement policy compliance checker for the City of Richmond. "
                            "Evaluate each numbered policy rule against the provided document data. "
                            "For each rule, return a verdict: COMPLIANT (document satisfies the policy), "
                            "VIOLATES (document clearly violates the policy), or INSUFFICIENT_DATA "
                            "(not enough information to determine). Provide evidence from the document "
                            "and a confidence score (0.0-1.0)."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"POLICY RULES:\n{rules_text}\n\n"
                            f"EXTRACTED FIELDS:\n{json.dumps(clean_fields, indent=2, default=str)}\n\n"
                            f"OCR TEXT (truncated):\n{truncated_ocr}"
                        ),
                    },
                ],
                response_format=schema,
                temperature=0.0,
                max_completion_tokens=800,
            )

            result = json.loads(response.choices[0].message.content)
            for evaluation in result.get("evaluations", []):
                if evaluation.get("verdict") != "VIOLATES":
                    continue

                rule_idx = evaluation.get("rule_number", 0) - 1
                if 0 <= rule_idx < len(batch):
                    rule = batch[rule_idx]
                    r_name = getattr(rule, "name", "") if not isinstance(rule, dict) else rule.get("name", "")
                    r_severity = getattr(rule, "severity", "warning") if not isinstance(rule, dict) else rule.get("severity", "warning")
                    r_suggestion = getattr(rule, "suggestion", None) if not isinstance(rule, dict) else rule.get("suggestion")
                    r_id = getattr(rule, "id", None) if not isinstance(rule, dict) else rule.get("id")
                    r_policy = getattr(rule, "policy_statement", "") if not isinstance(rule, dict) else rule.get("policy_statement", "")

                    res = _result(
                        rule_code=f"POLICY:{r_name}",
                        severity=r_severity,
                        field_name=None,
                        message=f"Semantic policy violation: {r_policy}",
                        suggestion=r_suggestion,
                    )
                    res["policy_rule_id"] = r_id
                    res["ai_evidence"] = evaluation.get("evidence", "")
                    res["ai_confidence"] = evaluation.get("confidence")
                    all_results.append(res)

        except Exception:
            logger.warning("Semantic policy evaluation failed for batch starting at %d", batch_start, exc_info=True)

    return all_results


async def validate_document(
    extracted_fields: dict,
    ocr_confidence: float,
    classification_confidence: float,
    custom_rules: list | None = None,
    ocr_text: str = "",
) -> list[dict]:
    """Run 13 rule-based checks + AI consistency + custom policy rules. Returns list of validation result dicts."""
    results = _run_rule_checks(extracted_fields, ocr_confidence, classification_confidence)
    ai_results = await _ai_consistency_check(extracted_fields)
    results.extend(ai_results)

    # Evaluate custom policy rules
    if custom_rules:
        deterministic = _evaluate_deterministic_rules(extracted_fields, custom_rules)
        results.extend(deterministic)

        semantic = await _evaluate_semantic_policies(extracted_fields, ocr_text, custom_rules)
        results.extend(semantic)

    logger.info(
        "Validation complete: %d issues (%d errors, %d warnings, %d info)",
        len(results),
        sum(1 for r in results if r["severity"] == "error"),
        sum(1 for r in results if r["severity"] == "warning"),
        sum(1 for r in results if r["severity"] == "info"),
    )
    return results
