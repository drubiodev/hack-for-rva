"""Document indexer — pushes extracted document data to Azure AI Search."""

import logging
import uuid
from datetime import datetime, timezone

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document, ExtractedFields

logger = logging.getLogger(__name__)


def _get_search_client() -> SearchClient:
    return SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index,
        credential=AzureKeyCredential(settings.azure_search_key),
    )


def _isoformat(val) -> str | None:
    """Convert date/datetime to ISO 8601 string for Azure Search."""
    if val is None:
        return None
    if isinstance(val, datetime):
        if val.tzinfo is None:
            val = val.replace(tzinfo=timezone.utc)
        return val.isoformat()
    # date object — convert to datetime at midnight UTC
    return datetime(val.year, val.month, val.day, tzinfo=timezone.utc).isoformat()


def _build_search_doc(doc: Document, ef: ExtractedFields) -> dict:
    """Build a search document dict from ORM models."""
    return {
        "id": str(doc.id),
        "title": ef.title or doc.filename,
        "vendor_name": ef.vendor_name,
        "document_type": doc.document_type,
        "status": doc.status,
        "primary_department": ef.primary_department,
        "department_tags": ef.department_tags or [],
        "total_amount": float(ef.total_amount) if ef.total_amount else None,
        "scope_summary": ef.scope_summary,
        "ocr_text": (doc.ocr_text or "")[:32000],
        "effective_date": _isoformat(ef.effective_date),
        "expiration_date": _isoformat(ef.expiration_date),
        "procurement_method": ef.procurement_method,
        "mbe_wbe_required": ef.mbe_wbe_required,
        "federal_funding": ef.federal_funding,
        "compliance_flags": ef.compliance_flags or [],
        "source": doc.source,
        "upload_date": _isoformat(doc.uploaded_at),
        "issuing_department": ef.issuing_department,
        "contract_type": ef.contract_type,
        "document_number": ef.document_number,
        "renewal_clause": ef.renewal_clause,
    }


async def index_document(document_id: uuid.UUID, db: AsyncSession) -> bool:
    """Index a single document in Azure AI Search. Returns True on success."""
    try:
        result = await db.execute(
            select(Document, ExtractedFields)
            .join(ExtractedFields, Document.id == ExtractedFields.document_id)
            .where(Document.id == document_id)
        )
        row = result.one_or_none()
        if not row:
            logger.warning("Cannot index document %s — not found or no extracted fields", document_id)
            return False

        doc, ef = row
        search_doc = _build_search_doc(doc, ef)

        client = _get_search_client()
        client.upload_documents(documents=[search_doc])
        logger.info("Indexed document %s in Azure AI Search", document_id)
        return True
    except Exception:
        logger.exception("Failed to index document %s", document_id)
        return False


async def index_batch(db: AsyncSession) -> int:
    """Reindex all processable documents. Returns count of indexed docs."""
    result = await db.execute(
        select(Document, ExtractedFields)
        .join(ExtractedFields, Document.id == ExtractedFields.document_id)
        .where(Document.status.notin_(["failed", "processing", "uploading", "error"]))
    )
    rows = list(result.all())

    if not rows:
        logger.info("No documents to index")
        return 0

    client = _get_search_client()
    batch = []
    indexed = 0

    for doc, ef in rows:
        batch.append(_build_search_doc(doc, ef))
        if len(batch) >= 100:
            try:
                client.upload_documents(documents=batch)
                indexed += len(batch)
            except Exception:
                logger.exception("Failed to index batch of %d documents", len(batch))
            batch = []

    if batch:
        try:
            client.upload_documents(documents=batch)
            indexed += len(batch)
        except Exception:
            logger.exception("Failed to index final batch of %d documents", len(batch))

    logger.info("Batch indexing complete: %d/%d documents indexed", indexed, len(rows))
    return indexed


async def delete_document_from_index(document_id: uuid.UUID) -> bool:
    """Remove a document from the search index."""
    try:
        client = _get_search_client()
        client.delete_documents(documents=[{"id": str(document_id)}])
        logger.info("Removed document %s from search index", document_id)
        return True
    except Exception:
        logger.exception("Failed to remove document %s from search index", document_id)
        return False
