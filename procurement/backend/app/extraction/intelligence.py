"""Document intelligence extraction — AI-powered risk, financial, clause, and compliance analysis."""

import json
import logging

from app.config import settings
from app.extraction.extractor import _smart_truncate

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# JSON schema for structured output
# ---------------------------------------------------------------------------

_INTELLIGENCE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "document_intelligence",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "executive_summary": {
                    "type": ["string", "null"],
                    "description": "2-3 sentence plain-English summary for non-technical staff. Cover what the document is, who it involves, and the key financial/risk takeaway.",
                },
                "risk_assessment": {
                    "type": "object",
                    "properties": {
                        "overall_risk_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                        },
                        "expiration_urgency": {
                            "type": "string",
                            "enum": ["none", "routine", "upcoming", "imminent", "expired"],
                        },
                        "insurance_gaps": {
                            "type": ["string", "null"],
                            "description": "Description of missing or insufficient insurance coverage, or null if adequate.",
                        },
                        "bonding_adequacy": {
                            "type": ["string", "null"],
                            "description": "Whether bond amounts are adequate relative to contract value, or null if N/A.",
                        },
                        "unusual_terms": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Unusual or non-standard contract terms that warrant attention.",
                        },
                        "liability_exposure": {
                            "type": ["string", "null"],
                            "description": "Summary of liability exposure (indemnification scope, limitation of liability).",
                        },
                        "termination_penalties": {
                            "type": ["string", "null"],
                            "description": "Penalties or costs for early termination, or null if none found.",
                        },
                        "risk_factors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Top 3-5 risk factors for this document.",
                        },
                    },
                    "required": [
                        "overall_risk_level", "expiration_urgency", "insurance_gaps",
                        "bonding_adequacy", "unusual_terms", "liability_exposure",
                        "termination_penalties", "risk_factors",
                    ],
                    "additionalProperties": False,
                },
                "financial_intelligence": {
                    "type": "object",
                    "properties": {
                        "cost_breakdown": {
                            "type": ["string", "null"],
                            "description": "Summary of cost structure (lump sum, unit rates, T&M, etc.).",
                        },
                        "rate_analysis": {
                            "type": ["string", "null"],
                            "description": "Key rates found (hourly, per-unit, etc.).",
                        },
                        "payment_milestones": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key payment milestones or schedule items.",
                        },
                        "escalation_clauses": {
                            "type": ["string", "null"],
                            "description": "Price escalation or adjustment clauses found.",
                        },
                        "budget_impact": {
                            "type": ["string", "null"],
                            "description": "Budget impact note (multi-year obligation, not-to-exceed, annual spend).",
                        },
                    },
                    "required": [
                        "cost_breakdown", "rate_analysis", "payment_milestones",
                        "escalation_clauses", "budget_impact",
                    ],
                    "additionalProperties": False,
                },
                "key_clauses": {
                    "type": "object",
                    "properties": {
                        "termination_conditions": {
                            "type": ["string", "null"],
                            "description": "Termination for convenience/cause conditions.",
                        },
                        "renewal_terms": {
                            "type": ["string", "null"],
                            "description": "Renewal mechanism (auto-renew, option years, mutual agreement).",
                        },
                        "indemnification": {
                            "type": ["string", "null"],
                            "description": "Indemnification scope and direction (mutual, one-way, etc.).",
                        },
                        "force_majeure": {
                            "type": ["string", "null"],
                            "description": "Force majeure clause presence and scope.",
                        },
                        "performance_metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "KPIs or performance standards specified.",
                        },
                        "liquidated_damages": {
                            "type": ["string", "null"],
                            "description": "Liquidated damages terms if present.",
                        },
                    },
                    "required": [
                        "termination_conditions", "renewal_terms", "indemnification",
                        "force_majeure", "performance_metrics", "liquidated_damages",
                    ],
                    "additionalProperties": False,
                },
                "compliance_intelligence": {
                    "type": "object",
                    "properties": {
                        "mbe_wbe_summary": {
                            "type": ["string", "null"],
                            "description": "MBE/WBE requirements summary with percentage targets.",
                        },
                        "federal_funding_implications": {
                            "type": ["string", "null"],
                            "description": "Federal funding implications (Davis-Bacon, Buy America, etc.).",
                        },
                        "prevailing_wage": {
                            "type": ["string", "null"],
                            "description": "Prevailing wage requirements if applicable.",
                        },
                        "ada_requirements": {
                            "type": ["string", "null"],
                            "description": "ADA compliance requirements if found.",
                        },
                        "environmental_requirements": {
                            "type": ["string", "null"],
                            "description": "Environmental compliance requirements if found.",
                        },
                        "compliance_risk_notes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific compliance risks or gaps identified.",
                        },
                    },
                    "required": [
                        "mbe_wbe_summary", "federal_funding_implications", "prevailing_wage",
                        "ada_requirements", "environmental_requirements", "compliance_risk_notes",
                    ],
                    "additionalProperties": False,
                },
                "opportunity_signals": {
                    "type": "object",
                    "properties": {
                        "consolidation_potential": {
                            "type": ["string", "null"],
                            "description": "Whether this contract could be consolidated with similar ones.",
                        },
                        "competitive_rebid": {
                            "type": ["string", "null"],
                            "description": "Whether this should be competitively rebid at renewal.",
                        },
                        "cooperative_purchasing": {
                            "type": ["string", "null"],
                            "description": "Cooperative purchasing opportunities (state contracts, GSA, etc.).",
                        },
                        "upcoming_actions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Recommended actions with approximate timeframes.",
                        },
                    },
                    "required": [
                        "consolidation_potential", "competitive_rebid",
                        "cooperative_purchasing", "upcoming_actions",
                    ],
                    "additionalProperties": False,
                },
            },
            "required": [
                "executive_summary", "risk_assessment", "financial_intelligence",
                "key_clauses", "compliance_intelligence", "opportunity_signals",
            ],
            "additionalProperties": False,
        },
    },
}

# ---------------------------------------------------------------------------
# Empty fallback (returned on failure)
# ---------------------------------------------------------------------------

EMPTY_INTELLIGENCE: dict = {
    "executive_summary": None,
    "risk_assessment": {
        "overall_risk_level": "medium",
        "expiration_urgency": "none",
        "insurance_gaps": None,
        "bonding_adequacy": None,
        "unusual_terms": [],
        "liability_exposure": None,
        "termination_penalties": None,
        "risk_factors": [],
    },
    "financial_intelligence": {
        "cost_breakdown": None,
        "rate_analysis": None,
        "payment_milestones": [],
        "escalation_clauses": None,
        "budget_impact": None,
    },
    "key_clauses": {
        "termination_conditions": None,
        "renewal_terms": None,
        "indemnification": None,
        "force_majeure": None,
        "performance_metrics": [],
        "liquidated_damages": None,
    },
    "compliance_intelligence": {
        "mbe_wbe_summary": None,
        "federal_funding_implications": None,
        "prevailing_wage": None,
        "ada_requirements": None,
        "environmental_requirements": None,
        "compliance_risk_notes": [],
    },
    "opportunity_signals": {
        "consolidation_potential": None,
        "competitive_rebid": None,
        "cooperative_purchasing": None,
        "upcoming_actions": [],
    },
}

# ---------------------------------------------------------------------------
# Fields summary builder
# ---------------------------------------------------------------------------


def _build_fields_summary(fields_dict: dict) -> str:
    """Build a concise summary of already-extracted fields for LLM context."""
    lines = []
    _field_keys = [
        ("vendor_name", "Vendor"),
        ("total_amount", "Total Amount"),
        ("effective_date", "Effective Date"),
        ("expiration_date", "Expiration Date"),
        ("issuing_department", "Department"),
        ("contract_type", "Contract Type"),
        ("payment_terms", "Payment Terms"),
        ("renewal_clause", "Renewal Clause"),
        ("insurance_required", "Insurance Required"),
        ("insurance_general_liability_min", "General Liability Min"),
        ("insurance_auto_liability_min", "Auto Liability Min"),
        ("insurance_professional_liability_min", "Professional Liability Min"),
        ("workers_comp_required", "Workers Comp Required"),
        ("bond_required", "Bond Required"),
        ("performance_bond_amount", "Performance Bond"),
        ("payment_bond_amount", "Payment Bond"),
        ("liquidated_damages_rate", "Liquidated Damages Rate"),
        ("mbe_wbe_required", "MBE/WBE Required"),
        ("mbe_wbe_details", "MBE/WBE Details"),
        ("federal_funding", "Federal Funding"),
        ("procurement_method", "Procurement Method"),
        ("scope_summary", "Scope"),
    ]
    for key, label in _field_keys:
        val = fields_dict.get(key)
        if val is not None and val != "" and val != []:
            if isinstance(val, float):
                lines.append(f"- {label}: ${val:,.2f}")
            else:
                lines.append(f"- {label}: {val}")
    return "\n".join(lines) if lines else "(no structured fields extracted)"


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------


async def extract_intelligence(
    ocr_text: str,
    document_type: str,
    fields_dict: dict,
) -> dict:
    """Extract document intelligence using Azure OpenAI.

    Args:
        ocr_text: Raw OCR text from Azure Document Intelligence.
        document_type: Classified document type (contract, rfp, etc.).
        fields_dict: Already-extracted structured fields.

    Returns:
        Intelligence dict matching the schema, or EMPTY_INTELLIGENCE on failure.
    """
    if not ocr_text or not ocr_text.strip():
        logger.warning("No OCR text for intelligence extraction — returning empty")
        return dict(EMPTY_INTELLIGENCE)

    if not settings.azure_openai_endpoint or not settings.azure_openai_key:
        logger.warning("Azure OpenAI not configured — skipping intelligence extraction")
        return dict(EMPTY_INTELLIGENCE)

    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        base_url=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_key,
    )

    truncated_text = _smart_truncate(ocr_text, budget=8000)
    fields_summary = _build_fields_summary(fields_dict)
    doc_type_label = document_type.replace("_", " ").title() if document_type else "Document"

    system_prompt = (
        "You are a senior procurement analyst for the City of Richmond, Virginia.\n"
        f"Given the OCR text and already-extracted structured fields from a {doc_type_label} document, "
        "produce a document intelligence report.\n\n"
        f"ALREADY-EXTRACTED FIELDS (use as reference, do not re-extract):\n{fields_summary}\n\n"
        "INSTRUCTIONS:\n"
        "- executive_summary: Write 2-3 plain-English sentences a non-technical city council member could understand.\n"
        "- risk_assessment: Evaluate contract risk considering expiration timeline, insurance adequacy, bonding, unusual terms, and liability.\n"
        '  - expiration_urgency: "expired" if past due, "imminent" if <30 days, "upcoming" if <90 days, "routine" if <365 days, "none" if >365 days or no date.\n'
        "- financial_intelligence: Analyze cost structure, rates, payment schedule, escalation clauses.\n"
        "- key_clauses: Identify critical legal/operational clauses. Quote briefly where helpful.\n"
        "- compliance_intelligence: Flag MBE/WBE, federal funding, prevailing wage, ADA, environmental requirements.\n"
        "- opportunity_signals: Identify savings opportunities, consolidation potential, rebid candidates.\n\n"
        "Rules:\n"
        "- Base ALL analysis on the document text. Do not invent facts.\n"
        "- Return null for fields where the document provides no relevant information.\n"
        "- Keep each field concise (1-3 sentences max).\n"
        "- The text may contain [...document continues...] gap markers — analyze all available sections."
    )

    try:
        response = await client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": truncated_text},
            ],
            temperature=0.0,
            max_completion_tokens=2000,
            response_format=_INTELLIGENCE_SCHEMA,
        )

        raw = response.choices[0].message.content
        if not raw:
            logger.warning("Empty response from intelligence extraction")
            return dict(EMPTY_INTELLIGENCE)

        result = json.loads(raw)
        logger.info("Intelligence extraction complete — risk_level=%s", result.get("risk_assessment", {}).get("overall_risk_level"))
        return result

    except Exception:
        logger.exception("Intelligence extraction failed")
        return dict(EMPTY_INTELLIGENCE)
