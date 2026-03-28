"""Seed script for demo — ingests Socrata CSV + processes all 10 pre-staged PDFs.

Usage:
    cd procurement/backend && .venv/bin/python -m scripts.seed_demo
"""

import asyncio
import glob
import logging
import os
import shutil
import tempfile
from datetime import date, timedelta

from sqlalchemy import func, select

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Base paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BACKEND_DIR))
PDF_DIR = os.path.join(
    PROJECT_ROOT, "pillar-thriving-city-hall", "procurement-examples", "pdfs"
)


async def seed_socrata():
    """Ingest Socrata CSV reusing the existing ingest logic."""
    from app.database import AsyncSessionLocal
    from app.models.document import Document, ExtractedFields
    from app.api.ingest import _download_csv, _parse_csv_rows, _build_dedup_key, _generate_filename, BATCH_SIZE

    logger.info("=== Socrata CSV Ingest ===")

    async with AsyncSessionLocal() as db:
        # Check how many socrata docs already exist
        existing_count_result = await db.execute(
            select(func.count(Document.id)).where(Document.source == "socrata")
        )
        existing_count = existing_count_result.scalar() or 0
        if existing_count > 0:
            logger.info("Socrata: %d records already exist, skipping download", existing_count)
            return existing_count

        # Download and parse
        logger.info("Downloading Socrata CSV...")
        csv_text = await _download_csv()
        parsed_rows = _parse_csv_rows(csv_text)
        logger.info("Parsed %d rows from CSV", len(parsed_rows))

        if not parsed_rows:
            logger.warning("No rows found in CSV")
            return 0

        from app.models.document import ActivityLog

        imported = 0
        batch_docs = []
        batch_fields = []

        for row_data in parsed_rows:
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
                extraction_confidence=1.0,
            )
            batch_fields.append(fields)
            imported += 1

            if len(batch_docs) >= BATCH_SIZE:
                db.add_all(batch_docs)
                db.add_all(batch_fields)
                await db.flush()
                batch_docs.clear()
                batch_fields.clear()
                logger.info("  Flushed %d records so far...", imported)

        if batch_docs:
            db.add_all(batch_docs)
            db.add_all(batch_fields)
            await db.flush()

        # Activity log
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
                details={"source": "socrata", "imported": imported},
            )
            db.add(activity)

        await db.commit()
        logger.info("Socrata: imported %d contracts", imported)
        return imported


async def seed_pdfs():
    """Upload and process all 10 pre-staged PDFs through the pipeline."""
    from app.database import AsyncSessionLocal
    from app.models.document import ActivityLog, Document
    from app.pipeline import process_document

    logger.info("=== PDF Pipeline Processing ===")

    pdf_files = sorted(glob.glob(os.path.join(PDF_DIR, "*.pdf")))
    if not pdf_files:
        logger.warning("No PDFs found in %s", PDF_DIR)
        return 0

    logger.info("Found %d PDFs in %s", len(pdf_files), PDF_DIR)

    processed = 0
    skipped = 0

    for pdf_path in pdf_files:
        original_filename = os.path.basename(pdf_path)

        # Check if already processed
        async with AsyncSessionLocal() as db:
            existing = await db.execute(
                select(Document).where(
                    Document.original_filename == original_filename,
                    Document.source == "upload",
                )
            )
            if existing.scalars().first():
                logger.info("  SKIP (exists): %s", original_filename)
                skipped += 1
                continue

        # Create document record
        async with AsyncSessionLocal() as db:
            doc = Document(
                filename=original_filename,
                original_filename=original_filename,
                source="upload",
                status="uploading",
                file_size_bytes=os.path.getsize(pdf_path),
                mime_type="application/pdf",
                submitted_by="demo-seed",
            )
            db.add(doc)
            await db.flush()

            activity = ActivityLog(
                document_id=doc.id,
                action="uploaded",
                actor_name="demo-seed",
                actor_role="analyst",
            )
            db.add(activity)
            await db.commit()

            doc_id = doc.id

        # Copy PDF to temp file (pipeline may clean up)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        shutil.copy2(pdf_path, tmp.name)
        tmp.close()

        logger.info("  Processing [%d/%d]: %s", processed + skipped + 1, len(pdf_files), original_filename)

        try:
            await process_document(doc_id, tmp.name, original_filename)
            processed += 1
            logger.info("  OK: %s", original_filename)
        except Exception:
            logger.exception("  FAILED: %s", original_filename)
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    logger.info("PDFs: %d processed, %d skipped", processed, skipped)
    return processed


async def seed_reminders():
    """Create sample reminders on contracts expiring soonest."""
    from app.database import AsyncSessionLocal
    from app.models.document import ContractReminder, Document, ExtractedFields

    logger.info("=== Creating Sample Reminders ===")

    async with AsyncSessionLocal() as db:
        # Check if reminders already exist
        existing = await db.execute(
            select(func.count(ContractReminder.id))
        )
        if (existing.scalar() or 0) > 0:
            logger.info("Reminders already exist, skipping")
            return

        # Find 2 contracts with expiration dates
        result = await db.execute(
            select(Document, ExtractedFields)
            .join(ExtractedFields, Document.id == ExtractedFields.document_id)
            .where(ExtractedFields.expiration_date.isnot(None))
            .order_by(ExtractedFields.expiration_date.asc())
            .limit(2)
        )
        rows = result.all()

        for doc, ef in rows:
            reminder_date = date.today() + timedelta(days=7)
            reminder = ContractReminder(
                document_id=doc.id,
                reminder_date=reminder_date,
                created_by="demo-seed",
                note=f"Review renewal for {ef.vendor_name or 'contract'} (expires {ef.expiration_date})",
                status="pending",
            )
            db.add(reminder)
            logger.info("  Reminder: %s on %s", ef.vendor_name or doc.filename, reminder_date)

        await db.commit()
        logger.info("Created %d sample reminders", len(rows))


async def main():
    from app.database import init_db

    logger.info("Initializing database tables...")
    await init_db()

    await seed_socrata()
    await seed_pdfs()
    await seed_reminders()

    logger.info("=== Demo seed complete! ===")


if __name__ == "__main__":
    asyncio.run(main())
