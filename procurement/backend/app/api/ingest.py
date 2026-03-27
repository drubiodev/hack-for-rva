"""Ingest router — endpoints for importing external data sources."""

import csv
import io
import logging
from datetime import date, datetime

import aiohttp
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document import ActivityLog, Document, ExtractedFields

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ingest", tags=["Ingest"])

SOCRATA_CSV_URL = (
    "https://data.richmondgov.com/api/views/xqn7-jvv2/rows.csv?accessType=DOWNLOAD"
)

# Batch size for bulk inserts
BATCH_SIZE = 200


def _parse_date(value: str | None) -> date | None:
    """Attempt to parse a date string in various formats.

    Returns None if the value is empty or unparseable.
    """
    if not value or not value.strip():
        return None
    value = value.strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_amount(value: str | None) -> float | None:
    """Parse a currency string like '$1,234.56' into a float."""
    if not value or not value.strip():
        return None
    cleaned = value.strip().replace("$", "").replace(",", "").replace(" ", "")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _normalize_header(header: str) -> str:
    """Lowercase and strip a CSV header for flexible matching."""
    return header.strip().lower().replace(" ", "_").replace("-", "_")


def _build_column_map(headers: list[str]) -> dict[str, int]:
    """Map normalized header names to their column index.

    This allows us to handle slight naming variations in the CSV
    without breaking.
    """
    return {_normalize_header(h): i for i, h in enumerate(headers)}


def _get_field(row: list[str], col_map: dict[str, int], *candidates: str) -> str | None:
    """Return the first matching column value from a row, or None."""
    for name in candidates:
        idx = col_map.get(name)
        if idx is not None and idx < len(row):
            val = row[idx].strip()
            if val:
                return val
    return None


def _generate_filename(row_data: dict) -> str:
    """Generate a descriptive filename from row data."""
    parts = []
    if row_data.get("document_number"):
        parts.append(row_data["document_number"])
    if row_data.get("vendor_name"):
        parts.append(row_data["vendor_name"][:40])
    if not parts:
        parts.append("socrata-contract")
    return "-".join(parts).replace(" ", "_").replace("/", "-") + ".csv"


def _build_dedup_key(row_data: dict) -> str:
    """Build a deduplication key from document_number or vendor+dates."""
    if row_data.get("document_number"):
        return f"socrata:{row_data['document_number']}"
    parts = [
        row_data.get("vendor_name", ""),
        str(row_data.get("effective_date", "")),
        str(row_data.get("expiration_date", "")),
    ]
    return f"socrata:{':'.join(parts)}"


async def _download_csv() -> str:
    """Download the Socrata CSV via aiohttp. Returns the CSV text."""
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(SOCRATA_CSV_URL) as resp:
            if resp.status != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to download Socrata CSV (HTTP {resp.status})",
                )
            return await resp.text()


def _parse_csv_rows(csv_text: str) -> list[dict]:
    """Parse CSV text into a list of structured row dicts.

    Returns a list of dicts with keys matching our schema fields,
    plus a 'raw' dict with all original columns.
    """
    reader = csv.reader(io.StringIO(csv_text))

    # Read header row
    try:
        headers = next(reader)
    except StopIteration:
        return []

    col_map = _build_column_map(headers)
    rows: list[dict] = []

    for row in reader:
        if not row or all(not cell.strip() for cell in row):
            continue  # skip blank rows

        # Build raw dict for storage
        raw = {}
        for i, h in enumerate(headers):
            if i < len(row):
                raw[h.strip()] = row[i].strip()

        # Extract mapped fields
        document_number = _get_field(
            row, col_map,
            "contract_number", "contract_no", "contract_#", "document_number",
            "contractnumber",
        )
        vendor_name = _get_field(
            row, col_map,
            "vendor_name", "vendor", "contractor", "company", "vendorname",
            "supplier",
        )
        issuing_department = _get_field(
            row, col_map,
            "department", "dept", "agency", "issuing_department",
            "department_name",
        )
        total_amount_str = _get_field(
            row, col_map,
            "contract_amount", "total_amount", "amount", "value",
            "contract_value", "contractamount", "total_contract_amount",
        )
        effective_date_str = _get_field(
            row, col_map,
            "start_date", "effective_date", "begin_date", "startdate",
            "contract_start_date",
        )
        expiration_date_str = _get_field(
            row, col_map,
            "end_date", "expiration_date", "expire_date", "enddate",
            "contract_end_date", "termination_date",
        )
        contract_type = _get_field(
            row, col_map,
            "contract_type", "type", "contracttype", "procurement_type",
        )
        title = _get_field(
            row, col_map,
            "description", "title", "contract_description", "purpose",
            "scope", "contract_title",
        )

        rows.append({
            "document_number": document_number,
            "vendor_name": vendor_name,
            "issuing_department": issuing_department,
            "total_amount": _parse_amount(total_amount_str),
            "effective_date": _parse_date(effective_date_str),
            "expiration_date": _parse_date(expiration_date_str),
            "contract_type": contract_type,
            "title": title,
            "raw": raw,
        })

    return rows


@router.post("/socrata")
async def ingest_socrata(db: AsyncSession = Depends(get_db)):
    """Import Socrata CSV into documents table.

    Downloads the City of Richmond contracts CSV from Socrata,
    parses each row, and creates Document + ExtractedFields records.
    Skips duplicates based on document_number or vendor+date composite key.
    """
    # 1. Download CSV
    try:
        csv_text = await _download_csv()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to download Socrata CSV")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to download Socrata CSV: {exc}",
        ) from exc

    # 2. Parse rows
    parsed_rows = _parse_csv_rows(csv_text)
    if not parsed_rows:
        return {"imported": 0, "skipped": 0, "message": "CSV was empty or had no data rows"}

    # 3. Load existing socrata document_numbers for dedup
    existing_result = await db.execute(
        select(ExtractedFields.document_number, ExtractedFields.vendor_name)
        .join(Document, Document.id == ExtractedFields.document_id)
        .where(Document.source == "socrata")
    )
    existing_rows = existing_result.all()

    # Build set of dedup keys already in DB
    existing_keys: set[str] = set()
    for ef_doc_num, ef_vendor in existing_rows:
        if ef_doc_num:
            existing_keys.add(f"socrata:{ef_doc_num}")
        elif ef_vendor:
            existing_keys.add(f"socrata:{ef_vendor}::")

    imported = 0
    skipped = 0
    batch_docs: list[Document] = []
    batch_fields: list[ExtractedFields] = []

    for row_data in parsed_rows:
        dedup_key = _build_dedup_key(row_data)
        if dedup_key in existing_keys:
            skipped += 1
            continue
        existing_keys.add(dedup_key)

        filename = _generate_filename(row_data)

        doc = Document(
            filename=filename,
            original_filename=filename,
            source="socrata",
            status="extracted",
            document_type="contract",
        )
        batch_docs.append(doc)

        fields = ExtractedFields(
            document=doc,
            title=row_data.get("title"),
            document_number=row_data.get("document_number"),
            vendor_name=row_data.get("vendor_name"),
            issuing_department=row_data.get("issuing_department"),
            total_amount=row_data.get("total_amount"),
            effective_date=row_data.get("effective_date"),
            expiration_date=row_data.get("expiration_date"),
            contract_type=row_data.get("contract_type"),
            raw_extraction=row_data.get("raw", {}),
            extraction_confidence=1.0,  # Socrata data is authoritative
        )
        batch_fields.append(fields)
        imported += 1

        # Flush in batches for performance
        if len(batch_docs) >= BATCH_SIZE:
            db.add_all(batch_docs)
            db.add_all(batch_fields)
            await db.flush()
            batch_docs.clear()
            batch_fields.clear()

    # Flush remaining
    if batch_docs:
        db.add_all(batch_docs)
        db.add_all(batch_fields)
        await db.flush()

    # 4. Create a single ActivityLog entry for the ingest (attach to first doc)
    if imported > 0:
        first_doc = (
            await db.execute(
                select(Document)
                .where(Document.source == "socrata")
                .order_by(Document.created_at.desc())
                .limit(1)
            )
        ).scalar_one()

        activity = ActivityLog(
            document_id=first_doc.id,
            action="extracted",
            actor_name="system",
            actor_role="system",
            details={
                "source": "socrata",
                "imported": imported,
                "skipped": skipped,
                "csv_url": SOCRATA_CSV_URL,
            },
        )
        db.add(activity)

    await db.commit()

    return {
        "imported": imported,
        "skipped": skipped,
        "message": f"Socrata ingest complete: {imported} imported, {skipped} skipped",
    }
