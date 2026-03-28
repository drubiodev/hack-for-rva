"""REST API router — all /api/v1 endpoints."""

import csv
import hashlib
import io
import math
import mimetypes
import os
import tempfile
import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Query, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, selectinload

from app.config import settings
from app.database import get_db
from app.models.document import ActivityLog, ContractReminder, Document, ExtractedFields, ValidationResult
from app.schemas.document import (
    ActivityEntrySchema,
    AnalyticsSummarySchema,
    AnnotationCreate,
    AnnotationResponse,
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
# Magic-bytes validation
# ---------------------------------------------------------------------------

_MAGIC_BYTES = {
    b"%PDF": {"application/pdf"},
    b"\x89PNG": {"image/png"},
    b"\xff\xd8\xff": {"image/jpeg", "image/jpg"},
    b"II\x2a\x00": {"image/tiff"},  # Little-endian TIFF
    b"MM\x00\x2a": {"image/tiff"},  # Big-endian TIFF
}


def _validate_magic_bytes(file_path: str, claimed_mime: str) -> bool:
    """Check if file content matches its claimed MIME type."""
    with open(file_path, "rb") as f:
        header = f.read(8)
    for magic, valid_mimes in _MAGIC_BYTES.items():
        if header.startswith(magic):
            return claimed_mime in valid_mimes or any(
                claimed_mime.startswith(m.split("/")[0]) for m in valid_mimes
            )
    return False


# ---------------------------------------------------------------------------
# Duplicate detection helper
# ---------------------------------------------------------------------------


def _compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Upload rate limiter (in-memory)
# ---------------------------------------------------------------------------

_upload_timestamps: dict[str, list[datetime]] = defaultdict(list)
_RATE_LIMIT = 5  # max uploads
_RATE_WINDOW = 300  # per 5 minutes (seconds)


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
    department: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List documents with optional filters and pagination."""
    query = select(Document).options(
        selectinload(Document.extracted_fields),
        selectinload(Document.validations),
        noload(Document.activity),
        noload(Document.reminders),
    )

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
    if department:
        query = query.where(
            Document.extracted_fields.has(ExtractedFields.primary_department == department)
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
        ef = doc.extracted_fields
        intel_kwargs: dict = {}
        if ef:
            vendor_name = ef.vendor_name
            total_amount = float(ef.total_amount) if ef.total_amount else None
            expiration_date = ef.expiration_date
            intel_kwargs = {
                "primary_department": ef.primary_department,
                "department_tags": ef.department_tags or [],
                "compliance_flags": ef.compliance_flags or [],
                "mbe_wbe_required": ef.mbe_wbe_required,
                "federal_funding": ef.federal_funding,
                "insurance_general_liability_min": float(ef.insurance_general_liability_min) if ef.insurance_general_liability_min else None,
                "bond_required": ef.bond_required,
                "procurement_method": ef.procurement_method,
                "cooperative_contract_ref": ef.cooperative_contract_ref,
            }

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
                **intel_kwargs,
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
    # Rate limiting
    now = datetime.now(timezone.utc)
    user_key = uploaded_by.lower().strip()
    _upload_timestamps[user_key] = [
        t for t in _upload_timestamps[user_key]
        if (now - t).total_seconds() < _RATE_WINDOW
    ]
    if len(_upload_timestamps[user_key]) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Too many uploads. Maximum {_RATE_LIMIT} uploads per {_RATE_WINDOW // 60} minutes.",
        )

    # Validate file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in settings.allowed_extension_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed: {settings.allowed_extensions}",
        )

    # Determine mime type
    mime_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/pdf"

    # Stream file to temp and validate size
    CHUNK_SIZE = 65536  # 64KB chunks
    max_bytes = settings.max_file_size_mb * 1024 * 1024

    suffix = ext or ".pdf"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    total_bytes = 0
    try:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > max_bytes:
                tmp.close()
                os.unlink(tmp.name)
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB",
                )
            tmp.write(chunk)
        tmp.close()
    except HTTPException:
        raise
    except Exception:
        tmp.close()
        os.unlink(tmp.name)
        raise

    # Validate magic bytes
    if not _validate_magic_bytes(tmp.name, mime_type):
        os.unlink(tmp.name)
        raise HTTPException(
            status_code=400,
            detail="File content does not match expected type. Ensure the file is a valid PDF, PNG, JPG, or TIFF.",
        )

    file_size_bytes = total_bytes

    # Duplicate detection via file hash
    file_hash = _compute_file_hash(tmp.name)
    dup_result = await db.execute(
        select(Document)
        .options(selectinload(Document.extracted_fields))
        .where(Document.file_hash == file_hash)
        .limit(1)
    )
    existing = dup_result.scalar_one_or_none()
    if existing:
        os.unlink(tmp.name)
        # Return existing document summary (skip extracted_fields lookup for simplicity)
        return DocumentSummary(
            id=existing.id,
            filename=existing.filename,
            original_filename=existing.original_filename,
            source=existing.source,
            status=existing.status,
            document_type=existing.document_type,
            vendor_name=None,
            total_amount=None,
            expiration_date=None,
            validation_error_count=0,
            validation_warning_count=0,
            submitted_by=existing.submitted_by,
            approved_by=existing.approved_by,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )

    # Record timestamp for rate limiting (only after all validation passes)
    _upload_timestamps[user_key].append(now)

    # Create document record
    doc = Document(
        filename=file.filename or "upload" + suffix,
        original_filename=file.filename,
        source="upload",
        status="uploading",
        file_size_bytes=file_size_bytes,
        mime_type=mime_type,
        submitted_by=uploaded_by,
        file_hash=file_hash,
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
# Annotations
# ---------------------------------------------------------------------------


@router.get(
    "/api/v1/documents/{document_id}/annotations",
    response_model=list[AnnotationResponse],
    tags=["Annotations"],
)
async def get_annotations(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all annotations for a document."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc.annotations or []


@router.post(
    "/api/v1/documents/{document_id}/annotations",
    response_model=AnnotationResponse,
    status_code=201,
    tags=["Annotations"],
)
async def create_annotation(
    document_id: UUID,
    body: AnnotationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add an annotation to a document."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    import uuid as _uuid

    annotation_id = "ann_" + _uuid.uuid4().hex[:12]
    now_iso = datetime.now(timezone.utc).isoformat()

    new_annotation = {
        "id": annotation_id,
        "x": body.x,
        "y": body.y,
        "page": body.page,
        "text": body.text,
        "author": body.author,
        "initials": body.initials,
        "time": now_iso,
    }

    doc.annotations = [*(doc.annotations or []), new_annotation]
    # Ensure SQLAlchemy detects the JSONB column change
    from sqlalchemy.orm.attributes import flag_modified
    try:
        flag_modified(doc, "annotations")
    except Exception:
        pass  # Not a tracked instance (e.g. in tests)

    activity = ActivityLog(
        document_id=doc.id,
        action="annotation_added",
        actor_name=body.author,
        actor_role="analyst",
        details={"annotation_id": annotation_id, "text": body.text},
    )
    db.add(activity)
    await db.commit()
    await db.refresh(doc)

    return new_annotation


@router.get(
    "/api/v1/documents/{document_id}/file",
    tags=["Documents"],
)
async def get_document_file(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Redirect to the original document file in blob storage."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.blob_url:
        raise HTTPException(status_code=404, detail="No file available for this document")
    return RedirectResponse(url=doc.blob_url)


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
    """Answer questions about procurement documents using AI + keyword search."""
    import uuid as _uuid
    from sqlalchemy import or_

    conversation_id = body.conversation_id or str(_uuid.uuid4())

    keywords = [w for w in body.question.lower().split() if len(w) > 2]
    if not keywords:
        return ChatResponse(
            answer="Please ask a more specific question about procurement documents.",
            sources=[],
            conversation_id=conversation_id,
        )

    # --- 1. Keyword ILIKE search for relevant documents (top 5) ---
    kw_query = (
        select(Document, ExtractedFields)
        .join(ExtractedFields, Document.id == ExtractedFields.document_id)
        .where(or_(*(Document.ocr_text.ilike(f"%{kw}%") for kw in keywords[:5])))
        .limit(5)
    )
    kw_result = await db.execute(kw_query)
    rows = list(kw_result.all())

    # --- 2. Also query contracts expiring within 90 days ---
    today = date.today()
    cutoff_90 = today + timedelta(days=90)
    expiring_result = await db.execute(
        select(Document, ExtractedFields)
        .join(ExtractedFields, Document.id == ExtractedFields.document_id)
        .where(ExtractedFields.expiration_date.isnot(None))
        .where(ExtractedFields.expiration_date >= today)
        .where(ExtractedFields.expiration_date <= cutoff_90)
        .order_by(ExtractedFields.expiration_date.asc())
        .limit(5)
    )
    expiring_rows = expiring_result.all()

    # Merge, dedup by document id
    seen_ids = {doc.id for doc, _ in rows}
    for doc, ef in expiring_rows:
        if doc.id not in seen_ids:
            rows.append((doc, ef))
            seen_ids.add(doc.id)

    # --- 3. Build context from matched documents ---
    sources = []
    context_parts = []
    for doc, ef in rows:
        sources.append(ChatSourceSchema(
            document_id=doc.id,
            title=ef.title or doc.filename,
            relevance=0.8,
        ))
        amount_str = f"${ef.total_amount:,.2f}" if ef.total_amount else "N/A"
        exp_str = str(ef.expiration_date) if ef.expiration_date else "N/A"
        eff_str = str(ef.effective_date) if ef.effective_date else "N/A"
        days_left = f" ({(ef.expiration_date - today).days} days)" if ef.expiration_date and ef.expiration_date >= today else ""
        context_parts.append(
            f"Document: {ef.title or doc.filename}\n"
            f"  Vendor: {ef.vendor_name or 'N/A'}\n"
            f"  Department: {ef.issuing_department or 'N/A'}\n"
            f"  Amount: {amount_str}\n"
            f"  Effective: {eff_str}\n"
            f"  Expires: {exp_str}{days_left}\n"
            f"  Type: {ef.contract_type or 'N/A'}\n"
            f"  Doc #: {ef.document_number or 'N/A'}"
        )

    # --- 4. Try AI-powered response if credentials are available ---
    ai_available = (
        settings.azure_openai_key != "PLACEHOLDER"
        and settings.azure_openai_endpoint != "https://PLACEHOLDER.openai.azure.com/"
    )

    if ai_available and context_parts:
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                base_url=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_key,
            )

            system_prompt = (
                "You are ContractIQ, an AI assistant for City of Richmond procurement staff.\n"
                "Answer questions about procurement documents using ONLY the context provided.\n"
                "If the answer isn't in the context, say so. Cite which document(s) your answer is based on.\n"
                "Never make legal compliance determinations — you are a decision-support tool.\n"
                "All information is AI-assisted and requires human review."
            )

            context_text = "\n\n".join(context_parts)
            user_message = f"Context:\n{context_text}\n\nQuestion: {body.question}"

            response = await client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_completion_tokens=500,
                temperature=0.3,
            )

            answer = response.choices[0].message.content or "No response generated."
            return ChatResponse(
                answer=answer,
                sources=sources,
                conversation_id=conversation_id,
            )
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("AI chat failed, falling back to keyword: %s", exc)

    # --- 5. Fallback: keyword-based response ---
    summaries = []
    for doc, ef in rows:
        amount_str = f"${ef.total_amount:,.2f}" if ef.total_amount else "N/A"
        exp_str = str(ef.expiration_date) if ef.expiration_date else "N/A"
        summaries.append(
            f"- **{ef.title or doc.filename}**: Vendor: {ef.vendor_name or 'N/A'}, "
            f"Amount: {amount_str}, Expires: {exp_str}"
        )

    if summaries:
        answer = (
            f"Found {len(summaries)} relevant document(s):\n\n"
            + "\n".join(summaries)
            + "\n\n*AI-assisted, requires human review.*"
        )
    else:
        answer = "No documents matched your query. Try different keywords."

    return ChatResponse(
        answer=answer,
        sources=sources,
        conversation_id=conversation_id,
    )
