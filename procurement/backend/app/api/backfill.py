"""Backfill intelligence fields for existing Socrata records using deterministic mapping."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document import Document, ExtractedFields

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ingest", tags=["Ingest"])

# --- Department mapping ---

_DEPARTMENT_MAP: dict[str, str] = {
    "public utilities": "PUBLIC_UTILITIES",
    "public works": "PUBLIC_WORKS",
    "city wide": "PROCUREMENT",
    "information technology": "INFORMATION_TECHNOLOGY",
    "human resources": "HUMAN_RESOURCES",
    "parks": "PARKS_RECREATION",
    "parks, recreation and community facilities": "PARKS_RECREATION",
    "police department": "PUBLIC_SAFETY",
    "police": "PUBLIC_SAFETY",
    "finance": "FINANCE",
    "planning & development review": "PLANNING_DEVELOPMENT",
    "planning and development review": "PLANNING_DEVELOPMENT",
    "emergency communication": "PUBLIC_SAFETY",
    "emergency communications": "PUBLIC_SAFETY",
    "fire and emergency services": "PUBLIC_SAFETY",
    "fire": "PUBLIC_SAFETY",
    "city attorney": "FINANCE",
    "sheriff's office": "PUBLIC_SAFETY",
    "sheriff": "PUBLIC_SAFETY",
    "procurement services": "PROCUREMENT",
    "dgs": "PUBLIC_WORKS",
    "department of general services": "PUBLIC_WORKS",
    "city council": "OTHER",
    "library": "COMMUNITY_DEVELOPMENT",
    "economic development": "COMMUNITY_DEVELOPMENT",
    "social services": "HUMAN_RESOURCES",
    "budget": "FINANCE",
    "city auditor": "FINANCE",
    "not listed": "OTHER",
}

# --- Procurement method mapping ---

_PROCUREMENT_MAP: dict[str, str] = {
    "invitation to bid": "COMPETITIVE_BID",
    "cooperative agreement": "COOPERATIVE_PURCHASE",
    "request for proposal": "RFP",
    "agency request": "SOLE_SOURCE",
    "small purchase": "COMPETITIVE_BID",
    "exempt purchase": "SOLE_SOURCE",
    "emergency": "EMERGENCY",
}


def map_department(issuing_dept: str | None) -> tuple[str, list[str]]:
    """Map a department name to (primary_department, department_tags)."""
    if not issuing_dept:
        return "OTHER", ["OTHER"]
    key = issuing_dept.strip().lower()
    # Try exact match first
    code = _DEPARTMENT_MAP.get(key)
    if code:
        return code, [code]
    # Try prefix match (handles "Parks, Recreation..." variations)
    for prefix, dept_code in _DEPARTMENT_MAP.items():
        if key.startswith(prefix):
            return dept_code, [dept_code]
    return "OTHER", ["OTHER"]


def map_procurement_method(procurement_type: str | None) -> str | None:
    """Map a procurement type string to a procurement_method enum."""
    if not procurement_type:
        return None
    key = procurement_type.strip().lower()
    return _PROCUREMENT_MAP.get(key)


def infer_compliance(
    solicitation_type: str | None,
    amount: float | None,
    procurement_method: str | None,
) -> dict:
    """Infer compliance flags, bond/insurance requirements from solicitation type and amount."""
    result: dict = {
        "compliance_flags": ["DRUG_FREE_WORKPLACE"],  # Standard for all City contracts
        "mbe_wbe_required": None,
        "federal_funding": None,
        "bond_required": None,
        "insurance_required": None,
        "workers_comp_required": None,
    }

    sol = (solicitation_type or "").lower()
    is_construction = "construction" in sol
    is_professional = "professional" in sol

    if is_construction:
        result["bond_required"] = True
        result["insurance_required"] = True
        result["workers_comp_required"] = True
        result["compliance_flags"].append("ENVIRONMENTAL")

    if is_professional:
        result["insurance_required"] = True

    # MBE/WBE: likely required for contracts > $100K via competitive bid or RFP
    if amount and amount > 100_000 and procurement_method in ("COMPETITIVE_BID", "RFP"):
        result["mbe_wbe_required"] = True
        if "MBE_WBE" not in result["compliance_flags"]:
            result["compliance_flags"].append("MBE_WBE")

    return result


def compute_intelligence(raw_extraction: dict, issuing_dept: str | None, amount: float | None) -> dict:
    """Compute all intelligence fields from raw CSV data. Returns dict of fields to set."""
    # Department — try issuing_dept first, fall back to raw CSV column
    dept_source = (
        issuing_dept
        or raw_extraction.get("Agency/Department")
        or raw_extraction.get("agency/department")
        or raw_extraction.get("Department")
        or raw_extraction.get("department")
    )
    primary_dept, dept_tags = map_department(dept_source)

    # Procurement method — from raw CSV "Procurement Type" column
    procurement_type_raw = (
        raw_extraction.get("Procurement Type")
        or raw_extraction.get("procurement_type")
        or raw_extraction.get("Type of Solicitation")
    )
    procurement_method = map_procurement_method(procurement_type_raw)

    # Solicitation type — for compliance inference
    solicitation_type = (
        raw_extraction.get("Type of Solicitation")
        or raw_extraction.get("type_of_solicitation")
    )
    compliance = infer_compliance(solicitation_type, amount, procurement_method)

    return {
        "primary_department": primary_dept,
        "department_tags": dept_tags,
        "department_confidence": 1.0,  # Authoritative source data
        "procurement_method": procurement_method,
        "cooperative_contract_ref": None,
        "prequalification_required": False,
        **compliance,
    }


BATCH_SIZE = 200


@router.post("/backfill-intelligence")
async def backfill_intelligence(db: AsyncSession = Depends(get_db)):
    """Backfill intelligence fields on Socrata records that have NULL primary_department."""
    # Find Socrata records missing intelligence
    query = (
        select(ExtractedFields)
        .join(Document, Document.id == ExtractedFields.document_id)
        .where(Document.source == "socrata")
        .where(ExtractedFields.primary_department.is_(None))
    )
    result = await db.execute(query)
    records = result.scalars().all()

    if not records:
        return {"updated": 0, "message": "No records need backfill"}

    updated = 0
    for ef in records:
        raw = ef.raw_extraction or {}
        intel = compute_intelligence(raw, ef.issuing_department, float(ef.total_amount) if ef.total_amount else None)

        ef.primary_department = intel["primary_department"]
        ef.department_tags = intel["department_tags"]
        ef.department_confidence = intel["department_confidence"]
        ef.procurement_method = intel["procurement_method"]
        ef.cooperative_contract_ref = intel["cooperative_contract_ref"]
        ef.prequalification_required = intel["prequalification_required"]
        ef.compliance_flags = intel["compliance_flags"]
        ef.mbe_wbe_required = intel["mbe_wbe_required"]
        ef.federal_funding = intel["federal_funding"]
        ef.bond_required = intel.get("bond_required") or ef.bond_required
        ef.insurance_required = intel.get("insurance_required") or ef.insurance_required
        ef.workers_comp_required = intel["workers_comp_required"]

        updated += 1
        if updated % BATCH_SIZE == 0:
            await db.flush()

    await db.commit()

    logger.info("Backfill complete: %d Socrata records updated with intelligence fields", updated)
    return {"updated": updated, "message": f"Backfilled intelligence on {updated} Socrata records"}
