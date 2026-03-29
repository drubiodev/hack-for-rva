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

from fastapi import APIRouter, BackgroundTasks, Depends, Form, Header, HTTPException, Query, Response, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, selectinload

from app.config import settings
from app.database import get_db
from app.models.document import (
    ActivityLog,
    ContractReminder,
    Document,
    ExtractedFields,
    ValidationResult,
    ValidationRuleAuditLog,
    ValidationRuleConfig,
)
from app.schemas.document import (
    ActivityEntrySchema,
    AnalyticsSummarySchema,
    AnnotationCreate,
    AnnotationResponse,
    ApproveRequest,
    ChatReferenceSchema,
    ChatRequest,
    ChatResponse,
    ChatSourceSchema,
    ComplianceSummary,
    DepartmentComplianceCard,
    DocumentDetail,
    DocumentListResponse,
    DocumentSummary,
    ErrorResponse,
    ExpiringContractSchema,
    ExtractedFieldsSchema,
    FieldUpdateRequest,
    RecentViolation,
    RejectRequest,
    ReminderCreateRequest,
    ReminderSchema,
    ReminderUpdateRequest,
    ReprocessRequest,
    RiskSummarySchema,
    SubmitRequest,
    TriggeredRuleSummary,
    ValidationResultSchema,
    ValidationRuleAuditLogSchema,
    ValidationRuleConfigCreate,
    ValidationRuleConfigSchema,
    ValidationRuleConfigUpdate,
)

router = APIRouter()


def _require_supervisor(x_user_role: str = Header(default="")) -> str:
    """Require supervisor role via X-User-Role header."""
    if x_user_role.lower() != "supervisor":
        raise HTTPException(status_code=403, detail="Supervisor role required")
    return x_user_role


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
    response: Response = None,
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
        if response is not None:
            response.status_code = 200  # 200 = duplicate (already processed), 202 = new upload
        ef = existing.extracted_fields
        # Count validations for the duplicate document
        val_counts = await db.execute(
            select(
                ValidationResult.severity,
                func.count(ValidationResult.id).label("n"),
            )
            .where(ValidationResult.document_id == existing.id)
            .group_by(ValidationResult.severity)
        )
        vc_map = {row.severity: row.n for row in val_counts}
        return DocumentSummary(
            id=existing.id,
            filename=existing.filename,
            original_filename=existing.original_filename,
            source=existing.source,
            status=existing.status,
            document_type=existing.document_type,
            vendor_name=ef.vendor_name if ef else None,
            total_amount=ef.total_amount if ef else None,
            expiration_date=ef.expiration_date if ef else None,
            validation_error_count=vc_map.get("error", 0),
            validation_warning_count=vc_map.get("warning", 0),
            submitted_by=existing.submitted_by,
            approved_by=existing.approved_by,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
            primary_department=ef.primary_department if ef else None,
            department_tags=ef.department_tags if ef else [],
            compliance_flags=ef.compliance_flags if ef else [],
            mbe_wbe_required=ef.mbe_wbe_required if ef else None,
            federal_funding=ef.federal_funding if ef else None,
            insurance_general_liability_min=ef.insurance_general_liability_min if ef else None,
            bond_required=ef.bond_required if ef else None,
            procurement_method=ef.procurement_method if ef else None,
            cooperative_contract_ref=ef.cooperative_contract_ref if ef else None,
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
    """Stream the original document file from blob storage (avoids CORS issues)."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.blob_url:
        raise HTTPException(status_code=404, detail="No file available for this document")

    # Placeholder/local-passthrough URLs are created when Azure Blob Storage is not
    # configured. There is nothing to proxy in that case.
    if "local-passthrough" in doc.blob_url.lower() or "placeholder" in doc.blob_url.lower():
        raise HTTPException(
            status_code=404,
            detail="Document file not available — Azure Blob Storage is not configured in this environment.",
        )

    import aiohttp
    from app.ocr.azure_blob import regenerate_sas_url

    try:
        fresh_url = regenerate_sas_url(doc.blob_url)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not generate a fresh SAS URL: {exc}")

    async def _stream():
        try:
            async with aiohttp.ClientSession() as http:
                async with http.get(fresh_url) as resp:
                    if resp.status != 200:
                        raise HTTPException(status_code=502, detail="Could not fetch document from storage")
                    async for chunk in resp.content.iter_chunked(65536):
                        yield chunk
        except aiohttp.ClientError as exc:
            raise HTTPException(status_code=502, detail=f"Storage error: {exc}")

    mime = doc.mime_type or "application/pdf"
    disposition = f'inline; filename="{doc.filename}"'
    return StreamingResponse(
        _stream(),
        media_type=mime,
        headers={
            "Content-Disposition": disposition,
            "Cache-Control": "private, max-age=300",
        },
    )


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
    background_tasks: BackgroundTasks,
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

    # Email notification to supervisors (fire-and-forget)
    from app.email.notifications import send_approval_request
    background_tasks.add_task(send_approval_request, document_id, body.submitted_by)

    return _doc_summary(doc)


@router.post(
    "/api/v1/documents/{document_id}/approve",
    response_model=DocumentSummary,
    tags=["Approvals"],
)
async def approve_document(
    document_id: UUID,
    body: ApproveRequest,
    background_tasks: BackgroundTasks,
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

    # Email notification to submitter (fire-and-forget)
    from app.email.notifications import send_approval_result as _send_approve
    background_tasks.add_task(_send_approve, document_id, True)

    return _doc_summary(doc)


@router.post(
    "/api/v1/documents/{document_id}/reject",
    response_model=DocumentSummary,
    tags=["Approvals"],
)
async def reject_document(
    document_id: UUID,
    body: RejectRequest,
    background_tasks: BackgroundTasks,
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

    # Email notification to submitter (fire-and-forget)
    from app.email.notifications import send_approval_result as _send_reject
    background_tasks.add_task(_send_reject, document_id, False)

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
# Intelligence endpoints — hardcoded analytics powered by SQL
# ---------------------------------------------------------------------------


@router.get("/api/v1/intelligence/department-spend", tags=["Intelligence"])
async def intelligence_department_spend(db: AsyncSession = Depends(get_db)):
    """Aggregated contract spend by department."""
    from app.search.client import sql_aggregation
    results = await sql_aggregation(db, aggregation="sum", aggregation_field="total_amount", group_by="primary_department")
    return {"departments": results}


@router.get("/api/v1/intelligence/expiring", tags=["Intelligence"])
async def intelligence_expiring(
    days: int = Query(90, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Documents expiring within N days."""
    from app.search.client import sql_expiring_contracts
    results = await sql_expiring_contracts(db, days_ahead=days)
    return {"documents": results, "days": days, "count": len(results)}


@router.get("/api/v1/intelligence/compliance-gaps", tags=["Intelligence"])
async def intelligence_compliance_gaps(db: AsyncSession = Depends(get_db)):
    """Documents with missing compliance fields (high-value contracts)."""
    from app.search.client import sql_compliance_gaps
    results = await sql_compliance_gaps(db)
    return {"gaps": results, "count": len(results)}


@router.get("/api/v1/intelligence/vendor-concentration", tags=["Intelligence"])
async def intelligence_vendor_concentration(db: AsyncSession = Depends(get_db)):
    """Vendors with multiple contracts — concentration risk analysis."""
    from app.search.client import sql_vendor_concentration
    results = await sql_vendor_concentration(db)
    return {"vendors": results, "count": len(results)}


@router.get("/api/v1/intelligence/sole-source-review", tags=["Intelligence"])
async def intelligence_sole_source_review(
    threshold: float = Query(50000, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Sole-source contracts above a dollar threshold."""
    from app.search.client import sql_filter_list
    results = await sql_filter_list(
        db,
        sql_filters={"procurement_method": "SOLE_SOURCE", "min_amount": threshold},
        limit=20,
    )
    return {"documents": results, "threshold": threshold, "count": len(results)}


# ---------------------------------------------------------------------------
# Admin — Search index management
# ---------------------------------------------------------------------------


@router.post("/api/v1/admin/reindex", tags=["Admin"])
async def admin_reindex(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(_require_supervisor),
):
    """Recreate search index and reindex all documents (supervisor only)."""
    from app.search.index_schema import create_or_update_index
    from app.search.indexer import index_batch

    # Create/update index schema first
    create_or_update_index()

    # Run batch indexing
    count = await index_batch(db)
    return {"detail": f"Reindex complete: {count} documents indexed"}


@router.post("/api/v1/admin/ensure-index", tags=["Admin"])
async def admin_ensure_index():
    """Create or update the Azure AI Search index schema."""
    from app.search.index_schema import create_or_update_index
    name = create_or_update_index()
    return {"detail": f"Index '{name}' created/updated"}


# ---------------------------------------------------------------------------
# Email admin — test, trigger, status
# ---------------------------------------------------------------------------


@router.post("/api/v1/admin/email/test", tags=["Admin"])
async def admin_email_test(to: str = Query(..., description="Recipient email")):
    """Send a test email to verify SMTP configuration."""
    from app.email.service import send_test_email
    success = await send_test_email(to)
    if success:
        return {"detail": f"Test email sent to {to}"}
    return {"detail": "Email sending failed — check logs and SMTP configuration"}


@router.post("/api/v1/admin/email/digest", tags=["Admin"])
async def admin_email_digest(db: AsyncSession = Depends(get_db)):
    """Manually trigger the daily expiration digest."""
    from app.email.notifications import send_expiration_digest
    success = await send_expiration_digest(db)
    return {"detail": "Digest sent" if success else "Digest skipped (no recipients or no expiring contracts)"}


@router.post("/api/v1/admin/email/compliance", tags=["Admin"])
async def admin_email_compliance(db: AsyncSession = Depends(get_db)):
    """Manually trigger the weekly compliance summary."""
    from app.email.notifications import send_weekly_compliance_summary
    success = await send_weekly_compliance_summary(db)
    return {"detail": "Compliance summary sent" if success else "Summary skipped (no recipients)"}


@router.get("/api/v1/admin/email/status", tags=["Admin"])
async def admin_email_status():
    """Return email configuration status (no secrets exposed)."""
    return {
        "email_enabled": settings.email_enabled,
        "smtp_host": settings.email_smtp_host,
        "smtp_port": settings.email_smtp_port,
        "from_address": settings.email_from_address,
        "digest_recipients_count": len(settings.email_digest_recipient_list),
        "alert_recipients_count": len(settings.email_alert_recipient_list),
        "supervisor_recipients_count": len(settings.email_supervisor_recipient_list),
        "user_map_count": len(settings.email_user_mapping),
        "digest_hour": settings.email_digest_hour,
        "digest_timezone": settings.email_digest_timezone,
        "weekly_day": settings.email_weekly_day,
    }


# ---------------------------------------------------------------------------
# Backfill — document intelligence for existing documents
# ---------------------------------------------------------------------------


@router.post("/api/v1/admin/backfill-intelligence", tags=["Admin"])
async def backfill_document_intelligence(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    """Backfill AI document intelligence for processed documents missing it."""
    from app.extraction.intelligence import extract_intelligence

    result = await db.execute(
        select(Document, ExtractedFields)
        .join(ExtractedFields, Document.id == ExtractedFields.document_id)
        .where(Document.status.notin_(["failed", "processing", "uploading", "error"]))
        .where(Document.ocr_text.isnot(None))
        .limit(limit)
    )
    rows = list(result.all())

    updated = 0
    skipped = 0
    for doc, ef in rows:
        metadata = doc.ocr_metadata or {}
        if metadata.get("intelligence"):
            skipped += 1
            continue

        try:
            intel = await extract_intelligence(
                doc.ocr_text,
                doc.document_type or "other",
                ef.raw_extraction or {},
            )
            metadata["intelligence"] = intel
            doc.ocr_metadata = metadata
            from sqlalchemy.orm.attributes import flag_modified
            try:
                flag_modified(doc, "ocr_metadata")
            except Exception:
                pass
            updated += 1
        except Exception as e:
            _logger.warning("Intelligence backfill failed for %s: %s", doc.id, e)

        if updated % 5 == 0 and updated > 0:
            await db.flush()

    await db.commit()
    return {"updated": updated, "skipped": skipped, "total_checked": len(rows)}


# ---------------------------------------------------------------------------
# Chat — AI-powered with semantic search + SQL intelligence via query router
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
    """Answer questions about procurement documents using AI query routing + semantic search."""
    import logging as _logging
    import uuid as _uuid

    from app.search.client import execute_query

    _logger = _logging.getLogger(__name__)
    conversation_id = body.conversation_id or str(_uuid.uuid4())

    if not body.question.strip():
        return ChatResponse(
            answer="Please ask a question about procurement documents.",
            sources=[],
            conversation_id=conversation_id,
        )

    # --- 1. Route query and retrieve context ---
    try:
        query_result = await execute_query(
            body.question, db,
            document_id=str(body.document_id) if body.document_id else None,
        )
    except Exception as exc:
        _logger.exception("Query execution failed: %s", exc)
        return ChatResponse(
            answer="Sorry, I encountered an error processing your question. Please try again.",
            sources=[],
            conversation_id=conversation_id,
        )

    intent = query_result["intent"]
    context_text = query_result["context"]
    raw_sources = query_result["sources"]

    # Build source schemas and numbered reference map
    sources = []
    references: list[ChatReferenceSchema] = []
    for idx, src in enumerate(raw_sources, 1):
        try:
            sources.append(ChatSourceSchema(
                document_id=src["id"],
                title=src.get("title"),
                relevance=src.get("relevance", 0.8),
                snippet=src.get("caption"),
            ))
            references.append(ChatReferenceSchema(
                index=idx,
                document_id=src["id"],
                title=src.get("title"),
                snippet=src.get("caption"),
            ))
        except Exception:
            pass  # skip malformed sources

    # Build numbered context for the LLM so it can cite [1], [2], etc.
    context_lines = context_text.split("\n\n") if context_text else []
    numbered_context_parts = []
    for i, line in enumerate(context_lines):
        ref_num = i + 1 if i < len(references) else None
        if ref_num:
            numbered_context_parts.append(f"[{ref_num}] {line}")
        else:
            numbered_context_parts.append(line)
    numbered_context = "\n\n".join(numbered_context_parts)

    # --- 2. Generate AI answer grounded in retrieved context ---
    ai_available = (
        settings.azure_openai_key != "PLACEHOLDER"
        and settings.azure_openai_endpoint != "https://PLACEHOLDER.openai.azure.com/"
    )

    if ai_available and (context_text or intent == "general_knowledge"):
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                base_url=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_key,
            )

            citation_instruction = ""
            if references:
                citation_instruction = (
                    "- IMPORTANT: When listing results or mentioning specific documents, "
                    "cite them using their reference number like [1], [2], etc. "
                    "Place the citation right after the document name or relevant fact. "
                    "Example: 'BP ENERGY COMPANY [1] has a contract worth $810M.'\n"
                )

            if intent == "document_scoped":
                system_prompt = (
                    "You are Mira, a courteous and professional procurement advisor serving City of Richmond "
                    "government officials and staff. Your role is to help officials understand procurement documents "
                    "clearly and confidently, so they can make well-informed decisions.\n\n"
                    "Persona guidelines:\n"
                    "- Address the user respectfully and professionally, as you would a senior government official.\n"
                    "- Write in clear, plain English — avoid jargon, bullet-point dumps, or overly terse answers.\n"
                    "- Begin responses with a brief, friendly orientation (e.g., 'Certainly! Here is a summary of this document.').\n"
                    "- Use flowing prose where possible; use structured lists only when enumerating multiple items.\n"
                    "- Format currency as dollars (e.g., $1,250,000) and dates in full (e.g., April 6, 2022).\n"
                    "- Do NOT use markdown symbols (**, ##, ---) in your response — plain text only.\n\n"
                    "Content rules:\n"
                    "- Answer ONLY from the document context provided. This is the ONLY document that matters.\n"
                    "- If information is not available, politely say so (e.g., 'The document does not specify this detail.').\n"
                    "- Do NOT reference or speculate about other documents or contracts.\n"
                    "- When the document has risk assessments, compliance findings, or key clauses, weave them into your answer naturally.\n"
                    "- If validation findings exist, surface relevant ones in a helpful, non-alarming tone.\n"
                    "- Close with a brief reminder that all information is AI-assisted and requires human review.\n"
                    "- Never make legal compliance determinations — you are a decision-support tool, not legal counsel."
                )
            else:
                system_prompt = (
                    "You are Mira, a courteous and professional procurement advisor serving City of Richmond "
                    "government officials and staff. Your role is to help officials understand procurement data, "
                    "contracts, and risks so they can make well-informed decisions.\n\n"
                    "Persona guidelines:\n"
                    "- Address the user respectfully and professionally, as you would a senior government official.\n"
                    "- Write in clear, plain English — avoid jargon, bullet-point dumps, or overly terse answers.\n"
                    "- Do NOT use markdown symbols (**, ##, ---) in your response — plain text only.\n\n"
                    "Content rules:\n"
                    "- Answer using ONLY the context provided. If the answer is not there, politely say so.\n"
                    f"{citation_instruction}"
                    "- For numerical aggregations, present numbers clearly (e.g., '42 contracts totaling $3.2 million').\n"
                    "- When risk assessments, key clauses, or financial intelligence are in the context, incorporate them naturally.\n"
                    "- Highlight HIGH or CRITICAL risk items in a clear but measured tone.\n"
                    "- Close with a brief reminder that all information is AI-assisted and requires human review.\n"
                    "- Never make legal compliance determinations — you are a decision-support tool, not legal counsel.\n\n"
                    f"Query intent: {intent}"
                )

            user_message = f"Context:\n{numbered_context}\n\nQuestion: {body.question}"

            response = await client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_completion_tokens=1200,
                temperature=0.3,
            )

            msg = response.choices[0].message
            answer = msg.content or ""
            # Some Azure OpenAI models return refusal or empty content
            if not answer and hasattr(msg, 'refusal') and msg.refusal:
                answer = f"I cannot answer this question: {msg.refusal}"
            elif not answer:
                _logger.warning("LLM returned empty content. Finish reason: %s, message: %s", response.choices[0].finish_reason, msg)
                answer = f"Based on the search results, I found {len(sources)} relevant documents. Please review the sources below for details.\n\n*AI-assisted, requires human review.*"
            return ChatResponse(
                answer=answer,
                sources=sources,
                conversation_id=conversation_id,
                intent=intent,
                references=references,
            )
        except Exception as exc:
            _logger.warning("AI answer generation failed, using context directly: %s", exc)

    # --- 3. Fallback: return context directly if AI unavailable ---
    if intent == "document_scoped" and context_text:
        # Build a clean, readable summary instead of dumping raw context markers
        import re as _re
        clean = context_text
        # Strip the [1] numbered prefix added for LLM citations
        clean = _re.sub(r"^\[1\]\s*", "", clean)
        # Strip non-printable / control characters (garbled OCR artifacts)
        clean = _re.sub(r"[^\x20-\x7E\n\r\t]", "", clean)
        # Replace === SECTION HEADERS === with plain headings (no markdown)
        clean = _re.sub(
            r"^=== (.+?) ===$",
            lambda m: f"\n{m.group(1).title()}",
            clean,
            flags=_re.MULTILINE,
        )
        # Collapse excessive blank lines
        clean = _re.sub(r"\n{3,}", "\n\n", clean).strip()
        # Cap length for readability
        if len(clean) > 3000:
            clean = clean[:3000] + "\n\n(Document content truncated. AI analysis is temporarily unavailable.)"
        answer = f"{clean}\n\nNote: All information is AI-assisted and requires human review."
    elif context_text:
        answer = f"{intent.replace('_', ' ').title()} results:\n\n{numbered_context}\n\nNote: All information is AI-assisted and requires human review."
    else:
        answer = "Thank you for your inquiry. No documents matched your query at this time. Please try different keywords or a more specific question."

    return ChatResponse(
        answer=answer,
        sources=sources,
        conversation_id=conversation_id,
        intent=intent,
        references=references,
    )


def _rule_to_dict(rule: ValidationRuleConfig) -> dict:
    """Snapshot a rule's mutable fields for audit logging."""
    return {
        "name": rule.name,
        "description": rule.description,
        "rule_type": rule.rule_type,
        "scope": rule.scope,
        "department": rule.department,
        "severity": rule.severity,
        "status": rule.status,
        "policy_statement": rule.policy_statement,
        "field_name": rule.field_name,
        "operator": rule.operator,
        "threshold_value": rule.threshold_value,
        "message_template": rule.message_template,
        "suggestion": rule.suggestion,
        "enabled": rule.enabled,
        "applies_to_doc_types": rule.applies_to_doc_types,
    }


# ---------------------------------------------------------------------------
# S7: Compliance Summary (must be registered BEFORE the {id} routes)
# ---------------------------------------------------------------------------


@router.get(
    "/api/v1/validation-rules/compliance-summary",
    response_model=ComplianceSummary,
    tags=["Validation Rules"],
)
async def get_compliance_summary(db: AsyncSession = Depends(get_db)):
    """Department-level compliance aggregates, top triggered rules, recent violations."""

    # Quick count — if zero policy violations, return empty summary fast
    total_viol_result = await db.execute(
        select(func.count(ValidationResult.id)).where(ValidationResult.policy_rule_id.isnot(None))
    )
    total_violations = total_viol_result.scalar() or 0

    active_rules_result = await db.execute(
        select(func.count(ValidationRuleConfig.id)).where(
            ValidationRuleConfig.status == "active",
            ValidationRuleConfig.enabled == True,  # noqa: E712
        )
    )
    total_rules_active = active_rules_result.scalar() or 0

    if total_violations == 0:
        return ComplianceSummary(
            department_cards=[],
            top_triggered_rules=[],
            recent_violations=[],
            total_violations=0,
            total_rules_active=total_rules_active,
        )

    # --- Department cards (only when violations exist) ---
    dept_query = (
        select(
            ExtractedFields.primary_department,
            ValidationResult.severity,
            func.count(ValidationResult.id).label("cnt"),
        )
        .select_from(ValidationResult)
        .outerjoin(ExtractedFields, ValidationResult.document_id == ExtractedFields.document_id)
        .where(ValidationResult.policy_rule_id.isnot(None))
        .group_by(ExtractedFields.primary_department, ValidationResult.severity)
    )
    dept_result = await db.execute(dept_query)
    dept_rows = dept_result.all()

    dept_map: dict[str, dict] = {}
    for dept, severity, cnt in dept_rows:
        dept_key = dept or "UNKNOWN"
        if dept_key not in dept_map:
            dept_map[dept_key] = {"department": dept_key, "error_count": 0, "warning_count": 0, "info_count": 0, "document_count": 0}
        if severity == "error":
            dept_map[dept_key]["error_count"] += cnt
        elif severity == "warning":
            dept_map[dept_key]["warning_count"] += cnt
        else:
            dept_map[dept_key]["info_count"] += cnt

    department_cards = [DepartmentComplianceCard(**d) for d in dept_map.values()]

    # --- Top triggered rules ---
    top_rules_query = (
        select(
            ValidationResult.policy_rule_id,
            ValidationResult.rule_code,
            ValidationResult.severity,
            func.count(ValidationResult.id).label("cnt"),
        )
        .where(ValidationResult.policy_rule_id.isnot(None))
        .group_by(ValidationResult.policy_rule_id, ValidationResult.rule_code, ValidationResult.severity)
        .order_by(func.count(ValidationResult.id).desc())
        .limit(10)
    )
    top_result = await db.execute(top_rules_query)
    top_triggered_rules = [
        TriggeredRuleSummary(rule_id=r[0], rule_code=r[1], severity=r[2], trigger_count=r[3])
        for r in top_result.all()
    ]

    # --- Recent violations ---
    recent_query = (
        select(ValidationResult)
        .where(ValidationResult.policy_rule_id.isnot(None))
        .order_by(ValidationResult.id.desc())
        .limit(10)
    )
    recent_result = await db.execute(recent_query)
    recent_violations = [
        RecentViolation(
            id=vr.id,
            document_id=vr.document_id,
            rule_code=vr.rule_code,
            severity=vr.severity,
            message=vr.message,
        )
        for vr in recent_result.scalars().all()
    ]

    return ComplianceSummary(
        department_cards=department_cards,
        top_triggered_rules=top_triggered_rules,
        recent_violations=recent_violations,
        total_violations=total_violations,
        total_rules_active=total_rules_active,
    )


# ---------------------------------------------------------------------------
# S7: Global Audit Log (must be registered BEFORE the {id} routes)
# ---------------------------------------------------------------------------


@router.get(
    "/api/v1/validation-rules/audit-log",
    tags=["Validation Rules"],
)
async def get_global_audit_log(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Global audit log across all validation rules with pagination."""
    total_result = await db.execute(select(func.count(ValidationRuleAuditLog.id)))
    total = total_result.scalar() or 0

    result = await db.execute(
        select(ValidationRuleAuditLog)
        .order_by(ValidationRuleAuditLog.changed_at.desc())
        .offset(offset)
        .limit(limit)
    )
    entries = result.scalars().all()
    items = [ValidationRuleAuditLogSchema.model_validate(e) for e in entries]
    return {"items": items, "total": total, "limit": limit, "offset": offset}


# ---------------------------------------------------------------------------
# S2: Validation Rules CRUD
# ---------------------------------------------------------------------------


@router.get(
    "/api/v1/validation-rules",
    response_model=list[ValidationRuleConfigSchema],
    tags=["Validation Rules"],
)
async def list_validation_rules(
    scope: str | None = Query(None),
    department: str | None = Query(None),
    status: str | None = Query(None),
    enabled: bool | None = Query(None),
    rule_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all validation rules with optional filters."""
    query = select(ValidationRuleConfig)
    if scope:
        query = query.where(ValidationRuleConfig.scope == scope)
    if department:
        query = query.where(ValidationRuleConfig.department == department)
    if status:
        query = query.where(ValidationRuleConfig.status == status)
    if enabled is not None:
        query = query.where(ValidationRuleConfig.enabled == enabled)
    if rule_type:
        query = query.where(ValidationRuleConfig.rule_type == rule_type)

    query = query.order_by(ValidationRuleConfig.created_at.desc())
    result = await db.execute(query)
    rules = result.scalars().all()
    return [ValidationRuleConfigSchema.model_validate(r) for r in rules]


@router.post(
    "/api/v1/validation-rules",
    response_model=ValidationRuleConfigSchema,
    status_code=201,
    tags=["Validation Rules"],
)
async def create_validation_rule(
    body: ValidationRuleConfigCreate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(_require_supervisor),
):
    """Create a new validation rule (supervisor only)."""
    # Validate rule_type-specific requirements
    if body.rule_type == "semantic_policy" and not body.policy_statement:
        raise HTTPException(
            status_code=400,
            detail="semantic_policy rules require a policy_statement",
        )
    if body.rule_type == "threshold":
        if not body.field_name or not body.operator or not body.threshold_value:
            raise HTTPException(
                status_code=400,
                detail="threshold rules require field_name, operator, and threshold_value",
            )

    rule = ValidationRuleConfig(
        name=body.name,
        description=body.description,
        rule_type=body.rule_type,
        scope=body.scope,
        department=body.department,
        severity=body.severity,
        status="draft",
        policy_statement=body.policy_statement,
        field_name=body.field_name,
        operator=body.operator,
        threshold_value=body.threshold_value,
        message_template=body.message_template,
        suggestion=body.suggestion,
        enabled=body.enabled,
        applies_to_doc_types=body.applies_to_doc_types,
        created_by=body.created_by,
    )
    db.add(rule)
    await db.flush()

    # Audit log
    audit = ValidationRuleAuditLog(
        rule_id=rule.id,
        rule_name=rule.name,
        action="created",
        changed_by=body.created_by,
        old_values={},
        new_values=_rule_to_dict(rule),
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rule)

    return ValidationRuleConfigSchema.model_validate(rule)


@router.patch(
    "/api/v1/validation-rules/{rule_id}",
    response_model=ValidationRuleConfigSchema,
    tags=["Validation Rules"],
)
async def update_validation_rule(
    rule_id: UUID,
    body: ValidationRuleConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(_require_supervisor),
):
    """Update a validation rule (supervisor only)."""
    result = await db.execute(
        select(ValidationRuleConfig).where(ValidationRuleConfig.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Validation rule not found")

    old_values = _rule_to_dict(rule)

    update_data = body.model_dump(exclude_unset=True)
    changed_by = update_data.pop("updated_by", None)

    for field, value in update_data.items():
        if hasattr(rule, field):
            setattr(rule, field, value)

    # Audit log
    audit = ValidationRuleAuditLog(
        rule_id=rule.id,
        rule_name=rule.name,
        action="updated",
        changed_by=changed_by,
        old_values=old_values,
        new_values=_rule_to_dict(rule),
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rule)

    return ValidationRuleConfigSchema.model_validate(rule)


@router.delete(
    "/api/v1/validation-rules/{rule_id}",
    tags=["Validation Rules"],
)
async def delete_validation_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(_require_supervisor),
):
    """Delete a validation rule. Soft-delete (deprecate) for active rules; hard-delete for draft."""
    result = await db.execute(
        select(ValidationRuleConfig).where(ValidationRuleConfig.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Validation rule not found")

    old_values = _rule_to_dict(rule)

    if rule.status == "draft":
        # Hard delete
        audit = ValidationRuleAuditLog(
            rule_id=rule.id,
            rule_name=rule.name,
            action="deleted",
            old_values=old_values,
            new_values={},
        )
        db.add(audit)
        await db.delete(rule)
        await db.commit()
        return {"detail": "Rule deleted"}
    else:
        # Soft delete: deprecate
        rule.status = "deprecated"
        rule.enabled = False
        audit = ValidationRuleAuditLog(
            rule_id=rule.id,
            rule_name=rule.name,
            action="deprecated",
            old_values=old_values,
            new_values=_rule_to_dict(rule),
        )
        db.add(audit)
        await db.commit()
        return {"detail": "Rule deprecated"}


@router.post(
    "/api/v1/validation-rules/{rule_id}/toggle",
    response_model=ValidationRuleConfigSchema,
    tags=["Validation Rules"],
)
async def toggle_validation_rule(
    rule_id: UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(_require_supervisor),
):
    """Toggle a rule's enabled flag (supervisor only)."""
    result = await db.execute(
        select(ValidationRuleConfig).where(ValidationRuleConfig.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Validation rule not found")

    old_values = _rule_to_dict(rule)
    rule.enabled = not rule.enabled

    audit = ValidationRuleAuditLog(
        rule_id=rule.id,
        rule_name=rule.name,
        action="toggled",
        changed_by=body.get("toggled_by"),
        old_values=old_values,
        new_values=_rule_to_dict(rule),
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rule)

    return ValidationRuleConfigSchema.model_validate(rule)


@router.post(
    "/api/v1/validation-rules/{rule_id}/activate",
    response_model=ValidationRuleConfigSchema,
    tags=["Validation Rules"],
)
async def activate_validation_rule(
    rule_id: UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(_require_supervisor),
):
    """Move a rule from draft to active (supervisor only)."""
    result = await db.execute(
        select(ValidationRuleConfig).where(ValidationRuleConfig.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Validation rule not found")
    if rule.status != "draft":
        raise HTTPException(status_code=400, detail=f"Cannot activate rule in status '{rule.status}'")

    old_values = _rule_to_dict(rule)
    rule.status = "active"

    audit = ValidationRuleAuditLog(
        rule_id=rule.id,
        rule_name=rule.name,
        action="activated",
        changed_by=body.get("activated_by"),
        old_values=old_values,
        new_values=_rule_to_dict(rule),
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rule)

    return ValidationRuleConfigSchema.model_validate(rule)


@router.post(
    "/api/v1/validation-rules/{rule_id}/deprecate",
    response_model=ValidationRuleConfigSchema,
    tags=["Validation Rules"],
)
async def deprecate_validation_rule(
    rule_id: UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(_require_supervisor),
):
    """Move a rule from active to deprecated (supervisor only)."""
    result = await db.execute(
        select(ValidationRuleConfig).where(ValidationRuleConfig.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Validation rule not found")
    if rule.status != "active":
        raise HTTPException(status_code=400, detail=f"Cannot deprecate rule in status '{rule.status}'")

    old_values = _rule_to_dict(rule)
    rule.status = "deprecated"
    rule.enabled = False

    audit = ValidationRuleAuditLog(
        rule_id=rule.id,
        rule_name=rule.name,
        action="deprecated",
        changed_by=body.get("deprecated_by"),
        old_values=old_values,
        new_values=_rule_to_dict(rule),
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rule)

    return ValidationRuleConfigSchema.model_validate(rule)


@router.get(
    "/api/v1/validation-rules/{rule_id}/audit-log",
    tags=["Validation Rules"],
)
async def get_rule_audit_log(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return audit log entries for a specific validation rule."""
    result = await db.execute(
        select(ValidationRuleAuditLog)
        .where(ValidationRuleAuditLog.rule_id == rule_id)
        .order_by(ValidationRuleAuditLog.changed_at.desc())
    )
    entries = result.scalars().all()
    return {"items": [ValidationRuleAuditLogSchema.model_validate(e) for e in entries]}
