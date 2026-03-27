"""REST API router — all /api/v1 endpoints."""

import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document import Document, ExtractedFields, ValidationResult
from app.schemas.document import (
    AnalyticsSummarySchema,
    DocumentDetail,
    DocumentListResponse,
    DocumentSummary,
    ErrorResponse,
    ExtractedFieldsSchema,
    FieldUpdateRequest,
    RiskSummarySchema,
    ValidationResultSchema,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@router.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


# ---------------------------------------------------------------------------
# Documents — List
# ---------------------------------------------------------------------------


@router.get(
    "/api/v1/documents",
    response_model=DocumentListResponse,
    tags=["Documents"],
)
async def list_documents(
    status: str | None = Query(None),
    document_type: str | None = Query(None),
    source: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List documents with optional filters and pagination."""
    query = select(Document)

    # Filters
    if status:
        query = query.where(Document.status == status)
    if document_type:
        query = query.where(Document.document_type == document_type)
    if source:
        query = query.where(Document.source == source)
    if search:
        like_pattern = f"%{search}%"
        query = query.where(
            Document.filename.ilike(like_pattern)
            | Document.original_filename.ilike(like_pattern)
        )

    # Total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Pagination
    total_pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size
    query = query.order_by(Document.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    documents = result.scalars().all()

    items = []
    for doc in documents:
        # Compute validation counts from loaded relationship
        error_count = sum(
            1 for v in doc.validations if v.severity == "error" and not v.resolved
        )
        warning_count = sum(
            1 for v in doc.validations if v.severity == "warning" and not v.resolved
        )

        # Get vendor_name and expiration_date from extracted_fields if available
        vendor_name = None
        total_amount = None
        expiration_date = None
        if doc.extracted_fields:
            vendor_name = doc.extracted_fields.vendor_name
            total_amount = float(doc.extracted_fields.total_amount) if doc.extracted_fields.total_amount else None
            expiration_date = doc.extracted_fields.expiration_date

        items.append(
            DocumentSummary(
                id=doc.id,
                filename=doc.filename,
                original_filename=doc.original_filename,
                source=doc.source,
                status=doc.status,
                document_type=doc.document_type,
                vendor_name=vendor_name,
                total_amount=total_amount,
                expiration_date=expiration_date,
                validation_error_count=error_count,
                validation_warning_count=warning_count,
                submitted_by=doc.submitted_by,
                approved_by=doc.approved_by,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
        )

    return DocumentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ---------------------------------------------------------------------------
# Documents — Detail
# ---------------------------------------------------------------------------


@router.get(
    "/api/v1/documents/{document_id}",
    response_model=DocumentDetail,
    responses={404: {"model": ErrorResponse}},
    tags=["Documents"],
)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get full document detail with extracted fields, validations, and activity."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    error_count = sum(
        1 for v in doc.validations if v.severity == "error" and not v.resolved
    )
    warning_count = sum(
        1 for v in doc.validations if v.severity == "warning" and not v.resolved
    )

    vendor_name = None
    total_amount = None
    expiration_date = None
    extracted_fields = None
    if doc.extracted_fields:
        vendor_name = doc.extracted_fields.vendor_name
        total_amount = float(doc.extracted_fields.total_amount) if doc.extracted_fields.total_amount else None
        expiration_date = doc.extracted_fields.expiration_date
        extracted_fields = ExtractedFieldsSchema.model_validate(doc.extracted_fields)

    validations = [ValidationResultSchema.model_validate(v) for v in doc.validations]
    from app.schemas.document import ActivityEntrySchema

    activity = [ActivityEntrySchema.model_validate(a) for a in doc.activity]

    return DocumentDetail(
        id=doc.id,
        filename=doc.filename,
        original_filename=doc.original_filename,
        source=doc.source,
        status=doc.status,
        document_type=doc.document_type,
        vendor_name=vendor_name,
        total_amount=total_amount,
        expiration_date=expiration_date,
        validation_error_count=error_count,
        validation_warning_count=warning_count,
        submitted_by=doc.submitted_by,
        approved_by=doc.approved_by,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        blob_url=doc.blob_url,
        file_size_bytes=doc.file_size_bytes,
        mime_type=doc.mime_type,
        page_count=doc.page_count,
        ocr_text=doc.ocr_text,
        ocr_confidence=float(doc.ocr_confidence) if doc.ocr_confidence else None,
        classification_confidence=float(doc.classification_confidence) if doc.classification_confidence else None,
        error_message=doc.error_message,
        submitted_at=doc.submitted_at,
        approved_at=doc.approved_at,
        rejection_reason=doc.rejection_reason,
        processed_at=doc.processed_at,
        extracted_fields=extracted_fields,
        validations=validations,
        activity=activity,
    )


# ---------------------------------------------------------------------------
# Stub endpoints — return 501 until implemented
# ---------------------------------------------------------------------------


@router.post(
    "/api/v1/documents/upload",
    status_code=202,
    response_model=DocumentSummary,
    tags=["Documents"],
)
async def upload_document():
    """Upload a PDF/image for processing. (Not yet implemented.)"""
    raise HTTPException(status_code=501, detail="Upload not yet implemented")


@router.patch(
    "/api/v1/documents/{document_id}/fields",
    response_model=ExtractedFieldsSchema,
    tags=["Documents"],
)
async def update_fields(document_id: UUID, body: FieldUpdateRequest):
    """Edit extracted fields. (Not yet implemented.)"""
    raise HTTPException(status_code=501, detail="Field update not yet implemented")


@router.post(
    "/api/v1/documents/{document_id}/submit",
    response_model=DocumentSummary,
    tags=["Approvals"],
)
async def submit_for_approval(document_id: UUID):
    """Submit document for supervisor approval. (Not yet implemented.)"""
    raise HTTPException(status_code=501, detail="Submit not yet implemented")


@router.post(
    "/api/v1/documents/{document_id}/approve",
    response_model=DocumentSummary,
    tags=["Approvals"],
)
async def approve_document(document_id: UUID):
    """Approve a document. (Not yet implemented.)"""
    raise HTTPException(status_code=501, detail="Approve not yet implemented")


@router.post(
    "/api/v1/documents/{document_id}/reject",
    response_model=DocumentSummary,
    tags=["Approvals"],
)
async def reject_document(document_id: UUID):
    """Reject a document. (Not yet implemented.)"""
    raise HTTPException(status_code=501, detail="Reject not yet implemented")


@router.post(
    "/api/v1/documents/{document_id}/reprocess",
    status_code=202,
    response_model=DocumentSummary,
    tags=["Documents"],
)
async def reprocess_document(document_id: UUID):
    """Re-run AI pipeline on document. (Not yet implemented.)"""
    raise HTTPException(status_code=501, detail="Reprocess not yet implemented")


@router.get(
    "/api/v1/analytics/summary",
    response_model=AnalyticsSummarySchema,
    tags=["Analytics"],
)
async def get_analytics_summary():
    """KPI summary. (Not yet implemented.)"""
    raise HTTPException(status_code=501, detail="Analytics not yet implemented")


@router.get(
    "/api/v1/analytics/risks",
    response_model=RiskSummarySchema,
    tags=["Analytics"],
)
async def get_risks(days: int = Query(90)):
    """Expiring contracts and risk alerts. (Not yet implemented.)"""
    raise HTTPException(status_code=501, detail="Risks not yet implemented")


@router.get(
    "/api/v1/activity",
    tags=["Activity"],
)
async def get_activity(limit: int = Query(50)):
    """Recent activity log. (Not yet implemented.)"""
    raise HTTPException(status_code=501, detail="Activity not yet implemented")


    # Socrata ingest endpoint moved to app/api/ingest.py
