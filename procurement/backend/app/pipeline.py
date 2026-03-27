"""Pipeline orchestrator: OCR -> classify -> extract -> validate -> save to DB."""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.document import ActivityLog, Document, ExtractedFields, ValidationResult
from app.ocr.azure_blob import upload_to_blob
from app.ocr.service import extract_text
from app.extraction.classifier import classify_document
from app.extraction.extractor import extract_fields
from app.validation.engine import validate_document

logger = logging.getLogger(__name__)


async def _log_activity(
    session,
    document_id: uuid.UUID,
    action: str,
    actor_role: str = "system",
    actor_name: str | None = None,
    details: dict | None = None,
):
    entry = ActivityLog(
        document_id=document_id,
        action=action,
        actor_name=actor_name,
        actor_role=actor_role,
        details=details or {},
    )
    session.add(entry)
    await session.flush()


async def process_document(
    document_id: uuid.UUID,
    file_path: str,
    original_filename: str | None = None,
):
    """Full processing pipeline: upload -> OCR -> classify -> extract -> validate."""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(Document).where(Document.id == document_id)
            )
            doc = result.scalar_one_or_none()
            if not doc:
                logger.error("Document %s not found", document_id)
                return

            # --- 1. Upload to blob storage ---
            doc.status = "uploading"
            await session.commit()

            blob_url = await upload_to_blob(file_path, doc.filename)
            doc.blob_url = blob_url
            await session.commit()

            # --- 2. OCR ---
            mime_type = doc.mime_type or "application/pdf"
            ocr_text, ocr_confidence = await extract_text(
                file_path, blob_url, mime_type, original_filename
            )
            doc.ocr_text = ocr_text
            doc.ocr_confidence = ocr_confidence
            doc.status = "ocr_complete"
            await session.commit()
            await _log_activity(session, document_id, "ocr_complete")
            await session.commit()

            if not ocr_text.strip():
                doc.status = "error"
                doc.error_message = "No text could be extracted from the document"
                await session.commit()
                return

            # --- 3. Classify ---
            document_type, classification_confidence = await classify_document(ocr_text)
            doc.document_type = document_type
            doc.classification_confidence = classification_confidence
            doc.status = "classified"
            await session.commit()
            await _log_activity(
                session,
                document_id,
                "classified",
                details={"document_type": document_type, "confidence": classification_confidence},
            )
            await session.commit()

            # --- 4. Extract fields ---
            fields_dict = await extract_fields(ocr_text, document_type)

            extracted = ExtractedFields(
                document_id=document_id,
                title=fields_dict.get("title"),
                document_number=fields_dict.get("document_number"),
                vendor_name=fields_dict.get("vendor_name"),
                issuing_department=fields_dict.get("issuing_department"),
                total_amount=fields_dict.get("total_amount"),
                currency=fields_dict.get("currency", "USD"),
                document_date=fields_dict.get("document_date"),
                effective_date=fields_dict.get("effective_date"),
                expiration_date=fields_dict.get("expiration_date"),
                contract_type=fields_dict.get("contract_type"),
                payment_terms=fields_dict.get("payment_terms"),
                renewal_clause=fields_dict.get("renewal_clause"),
                insurance_required=fields_dict.get("insurance_required"),
                bond_required=fields_dict.get("bond_required"),
                scope_summary=fields_dict.get("scope_summary"),
                raw_extraction=fields_dict,
                extraction_confidence=fields_dict.get("extraction_confidence"),
            )
            session.add(extracted)
            doc.status = "extracted"
            await session.commit()
            await _log_activity(session, document_id, "extracted")
            await session.commit()

            # --- 5. Validate ---
            validation_results = await validate_document(
                fields_dict, ocr_confidence, classification_confidence
            )
            for vr in validation_results:
                session.add(
                    ValidationResult(
                        document_id=document_id,
                        rule_code=vr["rule_code"],
                        severity=vr["severity"],
                        field_name=vr.get("field_name"),
                        message=vr["message"],
                        suggestion=vr.get("suggestion"),
                    )
                )
            await session.commit()

            # --- 6. Final status ---
            doc.status = "extracted"
            doc.processed_at = datetime.now(timezone.utc)
            await session.commit()

            logger.info("Pipeline complete for document %s", document_id)

        except Exception:
            logger.exception("Pipeline error for document %s", document_id)
            # Try to mark the document as errored
            try:
                result = await session.execute(
                    select(Document).where(Document.id == document_id)
                )
                doc = result.scalar_one_or_none()
                if doc:
                    doc.status = "error"
                    doc.error_message = "Processing pipeline failed unexpectedly"
                    await session.commit()
            except Exception:
                logger.exception("Failed to update error status for %s", document_id)
