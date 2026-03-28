"""REST API router — all /api/v1 endpoints."""

import csv
import io
import math
import mimetypes
import os
import tempfile
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.document import ActivityLog, ContractReminder, Document, ExtractedFields, ValidationResult
from app.schemas.document import (
    ActivityEntrySchema,
    AnalyticsSummarySchema,
    ApproveRequest,
    ChatRequest,
    ChatResponse,
    ChatSourceSchema,
    DocumentDetail,
    DocumentListResponse,
    DocumentSummary,
    ErrorResponse,
    ExpiringContractSchema,
    ExtractedFieldsSchema,
    FieldUpdateRequest,
    RejectRequest,
    ReminderCreateRequest,
    ReminderSchema,
    ReminderUpdateRequest,
    ReprocessRequest,
    RiskSummarySchema,
    SubmitRequest,
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
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    uploaded_by: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF/image for processing. Returns 202 and processes in background."""
    # Validate file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in settings.allowed_extension_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed: {settings.allowed_extensions}",
        )

    # Read file content and validate size
    content = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB",
        )

    # Determine mime type
    mime_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/pdf"

    # Save to temp file
    suffix = ext or ".pdf"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(content)
    tmp.close()

    # Create document record
    doc = Document(
        filename=file.filename or "upload" + suffix,
        original_filename=file.filename,
        source="upload",
        status="uploading",
        file_size_bytes=len(content),
        mime_type=mime_type,
        submitted_by=uploaded_by,
    )
    db.add(doc)
    await db.flush()

    # Log upload activity
    activity = ActivityLog(
        document_id=doc.id,
        action="uploaded",
        actor_name=uploaded_by,
        actor_role="analyst",
    )
    db.add(activity)
    await db.commit()

    # Trigger background processing
    from app.pipeline import process_document

    background_tasks.add_task(process_document, doc.id, tmp.name, file.filename)

    return DocumentSummary(
        id=doc.id,
        filename=doc.filename,
        original_filename=doc.original_filename,
        source=doc.source,
        status=doc.status,
        document_type=doc.document_type,
        vendor_name=None,
        total_amount=None,
        expiration_date=None,
        validation_error_count=0,
        validation_warning_count=0,
        submitted_by=doc.submitted_by,
        approved_by=doc.approved_by,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.patch(
    "/api/v1/documents/{document_id}/fields",
    response_model=ExtractedFieldsSchema,
    tags=["Documents"],
)
async def update_fields(
    document_id: UUID,
    body: FieldUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Edit extracted fields."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.extracted_fields:
        raise HTTPException(status_code=404, detail="No extracted fields for this document")

    ef = doc.extracted_fields
    changed_fields = {}
    for field_name, value in body.fields.items():
        if hasattr(ef, field_name):
            setattr(ef, field_name, value)
            changed_fields[field_name] = value

    activity = ActivityLog(
        document_id=doc.id,
        action="field_edited",
        actor_name=body.updated_by,
        actor_role="analyst",
        details={"changed_fields": changed_fields},
    )
    db.add(activity)
    await db.commit()
    await db.refresh(ef)

    return ExtractedFieldsSchema.model_validate(ef)


@router.post(
    "/api/v1/documents/{document_id}/review",
    response_model=DocumentSummary,
    tags=["Documents"],
)
async def review_document(
    document_id: UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    """Submit a review for a document."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.status = "extracted"

    activity = ActivityLog(
        document_id=doc.id,
        action="submitted",
        actor_name=body.get("reviewed_by"),
        actor_role=body.get("role", "analyst"),
        details={"notes": body.get("notes")},
    )
    db.add(activity)
    await db.commit()
    await db.refresh(doc)

    error_count = sum(1 for v in doc.validations if v.severity == "error" and not v.resolved)
    warning_count = sum(1 for v in doc.validations if v.severity == "warning" and not v.resolved)
    vendor_name = None
    total_amount = None
    expiration_date = None
    if doc.extracted_fields:
        vendor_name = doc.extracted_fields.vendor_name
        total_amount = float(doc.extracted_fields.total_amount) if doc.extracted_fields.total_amount else None
        expiration_date = doc.extracted_fields.expiration_date

    return DocumentSummary(
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


@router.get(
    "/api/v1/documents/{document_id}/export/csv",
    tags=["Documents"],
)
async def export_document_csv(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Export extracted fields as CSV."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.extracted_fields:
        raise HTTPException(status_code=404, detail="No extracted fields for this document")

    ef = doc.extracted_fields
    field_names = [
        "title", "document_number", "vendor_name", "issuing_department",
        "total_amount", "currency", "document_date", "effective_date",
        "expiration_date", "contract_type", "payment_terms", "renewal_clause",
        "insurance_required", "bond_required", "scope_summary",
    ]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(field_names)
    writer.writerow([getattr(ef, f, None) for f in field_names])

    output.seek(0)
    filename = f"{doc.filename.rsplit('.', 1)[0]}_fields.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/api/v1/documents/{document_id}/resolve-warning",
    response_model=ValidationResultSchema,
    tags=["Documents"],
)
async def resolve_warning(
    document_id: UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    """Resolve a validation warning."""
    validation_id = body.get("validation_id")
    resolved_by = body.get("resolved_by")
    if not validation_id or not resolved_by:
        raise HTTPException(status_code=400, detail="validation_id and resolved_by are required")

    result = await db.execute(
        select(ValidationResult).where(
            ValidationResult.id == validation_id,
            ValidationResult.document_id == document_id,
        )
    )
    vr = result.scalar_one_or_none()
    if not vr:
        raise HTTPException(status_code=404, detail="Validation result not found")

    vr.resolved = True
    vr.resolved_by = resolved_by
    vr.resolved_at = datetime.now(timezone.utc)

    activity = ActivityLog(
        document_id=document_id,
        action="warning_resolved",
        actor_name=resolved_by,
        actor_role="analyst",
        details={"validation_id": str(validation_id), "rule_code": vr.rule_code},
    )
    db.add(activity)
    await db.commit()
    await db.refresh(vr)

    return ValidationResultSchema.model_validate(vr)


# ---------------------------------------------------------------------------
# Helper — build DocumentSummary from a Document ORM object
# ---------------------------------------------------------------------------


def _doc_summary(doc: Document) -> DocumentSummary:
    error_count = sum(1 for v in doc.validations if v.severity == "error" and not v.resolved)
    warning_count = sum(1 for v in doc.validations if v.severity == "warning" and not v.resolved)
    vendor_name = None
    total_amount = None
    expiration_date = None
    if doc.extracted_fields:
        vendor_name = doc.extracted_fields.vendor_name
        total_amount = float(doc.extracted_fields.total_amount) if doc.extracted_fields.total_amount else None
        expiration_date = doc.extracted_fields.expiration_date
    return DocumentSummary(
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


# ---------------------------------------------------------------------------
# Approval Workflow
# ---------------------------------------------------------------------------


@router.post(
    "/api/v1/documents/{document_id}/submit",
    response_model=DocumentSummary,
    tags=["Approvals"],
)
async def submit_for_approval(
    document_id: UUID,
    body: SubmitRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit document for supervisor approval (analyst only)."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.status not in ("extracted", "analyst_review"):
        raise HTTPException(status_code=400, detail=f"Cannot submit document in status '{doc.status}'")

    doc.status = "pending_approval"
    doc.submitted_by = body.submitted_by
    doc.submitted_at = datetime.now(timezone.utc)

    activity = ActivityLog(
        document_id=doc.id,
        action="submitted",
        actor_name=body.submitted_by,
        actor_role="analyst",
    )
    db.add(activity)
    await db.commit()
    await db.refresh(doc)

    return _doc_summary(doc)


@router.post(
    "/api/v1/documents/{document_id}/approve",
    response_model=DocumentSummary,
    tags=["Approvals"],
)
async def approve_document(
    document_id: UUID,
    body: ApproveRequest,
    db: AsyncSession = Depends(get_db),
):
    """Approve a document (supervisor only)."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Cannot approve document in status '{doc.status}'")

    doc.status = "approved"
    doc.approved_by = body.approved_by
    doc.approved_at = datetime.now(timezone.utc)

    details = {}
    if body.comments:
        details["comments"] = body.comments

    activity = ActivityLog(
        document_id=doc.id,
        action="approved",
        actor_name=body.approved_by,
        actor_role="supervisor",
        details=details,
    )
    db.add(activity)
    await db.commit()
    await db.refresh(doc)

    return _doc_summary(doc)


@router.post(
    "/api/v1/documents/{document_id}/reject",
    response_model=DocumentSummary,
    tags=["Approvals"],
)
async def reject_document(
    document_id: UUID,
    body: RejectRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reject a document (supervisor only)."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Cannot reject document in status '{doc.status}'")

    doc.status = "rejected"
    doc.rejection_reason = body.reason

    activity = ActivityLog(
        document_id=doc.id,
        action="rejected",
        actor_name=body.rejected_by,
        actor_role="supervisor",
        details={"reason": body.reason},
    )
    db.add(activity)
    await db.commit()
    await db.refresh(doc)

    return _doc_summary(doc)


@router.post(
    "/api/v1/documents/{document_id}/reprocess",
    status_code=202,
    response_model=DocumentSummary,
    tags=["Documents"],
)
async def reprocess_document(
    document_id: UUID,
    body: ReprocessRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Re-run AI pipeline on document (supervisor only)."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.status = "uploading"

    activity = ActivityLog(
        document_id=doc.id,
        action="reprocessed",
        actor_name=body.requested_by,
        actor_role="supervisor",
    )
    db.add(activity)
    await db.commit()
    await db.refresh(doc)

    from app.pipeline import process_document
    background_tasks.add_task(process_document, doc.id, "", doc.original_filename)

    return _doc_summary(doc)


@router.get(
    "/api/v1/analytics/summary",
    response_model=AnalyticsSummarySchema,
    tags=["Analytics"],
)
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """KPI summary: total docs, by type/status/source, total value, processed today."""
    # Total documents
    total_result = await db.execute(select(func.count(Document.id)))
    total_documents = total_result.scalar() or 0

    # By type
    type_result = await db.execute(
        select(Document.document_type, func.count(Document.id))
        .where(Document.document_type.isnot(None))
        .group_by(Document.document_type)
    )
    by_type = {row[0]: row[1] for row in type_result.all()}

    # By status
    status_result = await db.execute(
        select(Document.status, func.count(Document.id)).group_by(Document.status)
    )
    by_status = {row[0]: row[1] for row in status_result.all()}

    # By source
    source_result = await db.execute(
        select(Document.source, func.count(Document.id)).group_by(Document.source)
    )
    by_source = {row[0]: row[1] for row in source_result.all()}

    # Total contract value
    value_result = await db.execute(
        select(func.coalesce(func.sum(ExtractedFields.total_amount), 0.0))
    )
    total_contract_value = float(value_result.scalar() or 0.0)

    # Documents processed today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.count(Document.id)).where(Document.processed_at >= today_start)
    )
    documents_processed_today = today_result.scalar() or 0

    return AnalyticsSummarySchema(
        total_documents=total_documents,
        by_type=by_type,
        by_status=by_status,
        by_source=by_source,
        total_contract_value=total_contract_value,
        documents_processed_today=documents_processed_today,
    )


@router.get(
    "/api/v1/analytics/risks",
    response_model=RiskSummarySchema,
    tags=["Analytics"],
)
async def get_risks(
    days: int = Query(90),
    db: AsyncSession = Depends(get_db),
):
    """Expiring contracts and risk alerts."""
    today = date.today()
    cutoff = today + timedelta(days=days)

    result = await db.execute(
        select(Document, ExtractedFields)
        .join(ExtractedFields, Document.id == ExtractedFields.document_id)
        .where(ExtractedFields.expiration_date.isnot(None))
        .where(ExtractedFields.expiration_date >= today)
        .where(ExtractedFields.expiration_date <= cutoff)
        .order_by(ExtractedFields.expiration_date.asc())
    )
    rows = result.all()

    expiring_contracts = []
    total_30 = 0
    total_60 = 0
    total_90 = 0

    for doc, ef in rows:
        days_until = (ef.expiration_date - today).days
        expiring_contracts.append(
            ExpiringContractSchema(
                id=doc.id,
                vendor_name=ef.vendor_name,
                title=ef.title,
                total_amount=float(ef.total_amount) if ef.total_amount else None,
                expiration_date=ef.expiration_date,
                days_until_expiry=days_until,
            )
        )
        if days_until <= 30:
            total_30 += 1
        if days_until <= 60:
            total_60 += 1
        if days_until <= 90:
            total_90 += 1

    # Check and trigger due reminders
    today_date = date.today()
    due_result = await db.execute(
        select(ContractReminder)
        .where(ContractReminder.reminder_date <= today_date)
        .where(ContractReminder.status == "pending")
    )
    due_reminders = due_result.scalars().all()
    for rem in due_reminders:
        rem.status = "triggered"
        rem.triggered_at = datetime.now(timezone.utc)
    if due_reminders:
        await db.commit()

    # Get all triggered (not yet dismissed) reminders
    triggered_result = await db.execute(
        select(ContractReminder, ExtractedFields)
        .join(Document, ContractReminder.document_id == Document.id)
        .outerjoin(ExtractedFields, Document.id == ExtractedFields.document_id)
        .where(ContractReminder.status == "triggered")
    )
    triggered_rows = triggered_result.all()
    triggered_reminders = []
    for rem, ef in triggered_rows:
        triggered_reminders.append(ReminderSchema(
            id=rem.id, document_id=rem.document_id,
            reminder_date=rem.reminder_date, created_by=rem.created_by,
            note=rem.note, status=rem.status,
            created_at=rem.created_at, triggered_at=rem.triggered_at,
            vendor_name=ef.vendor_name if ef else None,
            title=ef.title if ef else None,
            expiration_date=ef.expiration_date if ef else None,
        ))

    # Count pending reminders
    pending_count_result = await db.execute(
        select(func.count(ContractReminder.id)).where(ContractReminder.status == "pending")
    )
    pending_count = pending_count_result.scalar() or 0

    return RiskSummarySchema(
        expiring_contracts=expiring_contracts,
        total_expiring_30=total_30,
        total_expiring_60=total_60,
        total_expiring_90=total_90,
        triggered_reminders=triggered_reminders,
        pending_reminders_count=pending_count,
    )


@router.get(
    "/api/v1/activity",
    tags=["Activity"],
)
async def get_activity(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Recent activity log across all documents."""
    result = await db.execute(
        select(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
    )
    entries = result.scalars().all()
    return {"items": [ActivityEntrySchema.model_validate(e) for e in entries]}


# ---------------------------------------------------------------------------
# Reminders
# ---------------------------------------------------------------------------


@router.post(
    "/api/v1/documents/{document_id}/reminders",
    status_code=201,
    response_model=ReminderSchema,
    tags=["Reminders"],
)
async def create_reminder(
    document_id: UUID,
    body: ReminderCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a renewal reminder for a document."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    reminder = ContractReminder(
        document_id=document_id,
        reminder_date=body.reminder_date,
        created_by=body.created_by,
        note=body.note,
        status="pending",
    )
    db.add(reminder)

    activity = ActivityLog(
        document_id=document_id,
        action="reminder_set",
        actor_name=body.created_by,
        actor_role="analyst",
        details={"reminder_date": str(body.reminder_date), "note": body.note},
    )
    db.add(activity)
    await db.commit()
    await db.refresh(reminder)

    # Build response with joined fields
    ef = doc.extracted_fields
    return ReminderSchema(
        id=reminder.id,
        document_id=reminder.document_id,
        reminder_date=reminder.reminder_date,
        created_by=reminder.created_by,
        note=reminder.note,
        status=reminder.status,
        created_at=reminder.created_at,
        triggered_at=reminder.triggered_at,
        vendor_name=ef.vendor_name if ef else None,
        title=ef.title if ef else None,
        expiration_date=ef.expiration_date if ef else None,
    )


@router.get(
    "/api/v1/reminders",
    tags=["Reminders"],
)
async def list_reminders(
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List contract reminders with optional status filter."""
    query = (
        select(ContractReminder, ExtractedFields)
        .join(Document, ContractReminder.document_id == Document.id)
        .outerjoin(ExtractedFields, Document.id == ExtractedFields.document_id)
    )
    if status:
        query = query.where(ContractReminder.status == status)
    query = query.order_by(ContractReminder.reminder_date.asc()).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    items = []
    for rem, ef in rows:
        items.append(ReminderSchema(
            id=rem.id, document_id=rem.document_id,
            reminder_date=rem.reminder_date, created_by=rem.created_by,
            note=rem.note, status=rem.status,
            created_at=rem.created_at, triggered_at=rem.triggered_at,
            vendor_name=ef.vendor_name if ef else None,
            title=ef.title if ef else None,
            expiration_date=ef.expiration_date if ef else None,
        ))
    return {"items": items}


@router.patch(
    "/api/v1/reminders/{reminder_id}",
    response_model=ReminderSchema,
    tags=["Reminders"],
)
async def update_reminder(
    reminder_id: UUID,
    body: ReminderUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update reminder status (e.g. dismiss a triggered reminder)."""
    result = await db.execute(
        select(ContractReminder).where(ContractReminder.id == reminder_id)
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    reminder.status = body.status

    if body.status == "dismissed":
        activity = ActivityLog(
            document_id=reminder.document_id,
            action="reminder_dismissed",
            actor_name=body.dismissed_by,
            actor_role="analyst",
            details={"reminder_id": str(reminder_id)},
        )
        db.add(activity)

    await db.commit()
    await db.refresh(reminder)

    # Join with extracted fields for response
    ef_result = await db.execute(
        select(ExtractedFields).where(ExtractedFields.document_id == reminder.document_id)
    )
    ef = ef_result.scalar_one_or_none()

    return ReminderSchema(
        id=reminder.id, document_id=reminder.document_id,
        reminder_date=reminder.reminder_date, created_by=reminder.created_by,
        note=reminder.note, status=reminder.status,
        created_at=reminder.created_at, triggered_at=reminder.triggered_at,
        vendor_name=ef.vendor_name if ef else None,
        title=ef.title if ef else None,
        expiration_date=ef.expiration_date if ef else None,
    )


# ---------------------------------------------------------------------------
# Chat (keyword-search stub — upgrade to Azure AI Search RAG later)
# ---------------------------------------------------------------------------


@router.post(
    "/api/v1/chat",
    response_model=ChatResponse,
    tags=["Chat"],
)
async def chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Answer questions about procurement documents using keyword search."""
    import uuid as _uuid

    keywords = [w for w in body.question.lower().split() if len(w) > 2]
    if not keywords:
        return ChatResponse(
            answer="Please ask a more specific question about procurement documents.",
            sources=[],
            conversation_id=body.conversation_id or str(_uuid.uuid4()),
        )

    # Search documents by keyword matches in OCR text
    query = select(Document, ExtractedFields).join(
        ExtractedFields, Document.id == ExtractedFields.document_id
    )
    conditions = []
    for kw in keywords[:5]:
        conditions.append(Document.ocr_text.ilike(f"%{kw}%"))

    if conditions:
        from sqlalchemy import or_
        query = query.where(or_(*conditions))

    query = query.limit(5)
    result = await db.execute(query)
    rows = result.all()

    sources = []
    summaries = []
    for doc, ef in rows:
        sources.append(ChatSourceSchema(
            document_id=doc.id,
            title=ef.title or doc.filename,
            relevance=0.8,
        ))
        amount_str = f"${ef.total_amount:,.2f}" if ef.total_amount else "N/A"
        exp_str = str(ef.expiration_date) if ef.expiration_date else "N/A"
        summaries.append(
            f"- **{ef.title or doc.filename}**: Vendor: {ef.vendor_name or 'N/A'}, "
            f"Amount: {amount_str}, Expires: {exp_str}"
        )

    if summaries:
        answer = f"Found {len(summaries)} relevant document(s):\n\n" + "\n".join(summaries)
    else:
        answer = "No documents matched your query. Try different keywords."

    return ChatResponse(
        answer=answer,
        sources=sources,
        conversation_id=body.conversation_id or str(_uuid.uuid4()),
    )


    # Socrata ingest endpoint moved to app/api/ingest.py
