"""Pipeline orchestrator: OCR -> classify -> extract -> validate -> save to DB."""

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from pathlib import Path

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.document import ActivityLog, Document, ExtractedFields, ValidationResult
from app.ocr.azure_blob import upload_to_blob
from app.ocr.service import extract_text
from app.extraction.classifier import classify_document
from app.extraction.extractor import extract_fields
from app.validation.engine import validate_document

logger = logging.getLogger(__name__)

# Limit concurrent document processing to prevent resource exhaustion
_pipeline_semaphore = asyncio.Semaphore(3)


async def _retry_async(coro_factory, max_attempts=3, base_delay=2.0, operation="operation"):
    """Retry an async operation with exponential backoff."""
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await coro_factory()
        except Exception as e:
            last_error = e
            if attempt < max_attempts:
                delay = base_delay * (2 ** (attempt - 1))
                logger.warning("%s failed (attempt %d/%d): %s — retrying in %.1fs", operation, attempt, max_attempts, e, delay)
                await asyncio.sleep(delay)
            else:
                logger.error("%s failed after %d attempts: %s", operation, max_attempts, e)
    raise last_error


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
    async with _pipeline_semaphore:
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
            try:
                ocr_text, ocr_confidence = await _retry_async(
                    lambda: extract_text(file_path, blob_url, mime_type, original_filename),
                    operation="OCR",
                )
            except Exception as e:
                doc.status = "error"
                doc.error_message = f"OCR failed after 3 retries: {type(e).__name__}: {str(e)[:200]}"
                await session.commit()
                return

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

            # --- 3. Classify (with demo cache shortcut) ---
            _demo_cached_extraction = None
            _is_demo = "PLACEHOLDER" in settings.azure_openai_key and original_filename
            if _is_demo:
                from fixtures.demo_cache import DEMO_CLASSIFICATIONS, DEMO_EXTRACTIONS
                stem = Path(original_filename).stem
                if stem in DEMO_CLASSIFICATIONS:
                    document_type, classification_confidence = DEMO_CLASSIFICATIONS[stem]
                    _demo_cached_extraction = DEMO_EXTRACTIONS.get(stem)
                    logger.info("Using demo cache for classification: %s -> %s", stem, document_type)
                else:
                    document_type, classification_confidence = ("other", 0.0)
                    logger.info("Demo mode but no cache for %s — defaulting to other", stem)
            else:
                try:
                    document_type, classification_confidence = await _retry_async(
                        lambda: classify_document(ocr_text),
                        operation="Classification",
                    )
                except Exception as e:
                    doc.status = "error"
                    doc.error_message = f"Classification failed after 3 retries: {type(e).__name__}: {str(e)[:200]}"
                    await session.commit()
                    return

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

            # --- 4. Extract fields (with demo cache shortcut) ---
            if _demo_cached_extraction:
                fields_dict = dict(_demo_cached_extraction)
                logger.info("Using demo cache for extraction: %s", Path(original_filename).stem)
            else:
                try:
                    fields_dict = await _retry_async(
                        lambda: extract_fields(ocr_text, document_type),
                        operation="Field extraction",
                    )
                except Exception as e:
                    doc.status = "error"
                    doc.error_message = f"Field extraction failed after 3 retries: {type(e).__name__}: {str(e)[:200]}"
                    await session.commit()
                    return

            # Parse date strings to date objects
            def _parse_date(val):
                if val is None:
                    return None
                if isinstance(val, str):
                    try:
                        from datetime import date as _date
                        return _date.fromisoformat(val)
                    except (ValueError, TypeError):
                        return None
                return val

            extracted = ExtractedFields(
                document_id=document_id,
                title=fields_dict.get("title"),
                document_number=fields_dict.get("document_number"),
                vendor_name=fields_dict.get("vendor_name"),
                issuing_department=fields_dict.get("issuing_department"),
                total_amount=fields_dict.get("total_amount"),
                currency=fields_dict.get("currency", "USD"),
                document_date=_parse_date(fields_dict.get("document_date")),
                effective_date=_parse_date(fields_dict.get("effective_date")),
                expiration_date=_parse_date(fields_dict.get("expiration_date")),
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
            # Pass document_type so validation can check contract-specific rules
            fields_dict["_document_type"] = document_type
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
