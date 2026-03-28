"""Tests for Phase 3 review endpoints: field edit, review, CSV export, resolve warning."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database import get_db
from app.main import app
from app.models.document import ActivityLog, Document, ExtractedFields, ValidationResult


def _make_extracted_fields(doc_id, **overrides):
    """Create a mock ExtractedFields with sensible defaults."""
    defaults = {
        "id": uuid.uuid4(),
        "document_id": doc_id,
        "title": "Test Contract",
        "document_number": "C-1001",
        "vendor_name": "Acme Corp",
        "issuing_department": "Public Works",
        "total_amount": 50000.0,
        "currency": "USD",
        "document_date": None,
        "effective_date": None,
        "expiration_date": None,
        "contract_type": "Services",
        "payment_terms": "Net 30",
        "renewal_clause": None,
        "insurance_required": True,
        "bond_required": False,
        "scope_summary": "Road maintenance",
        "department_tags": ["PUBLIC_WORKS"],
        "primary_department": "PUBLIC_WORKS",
        "department_confidence": 0.95,
        "mbe_wbe_required": None,
        "mbe_wbe_details": None,
        "federal_funding": None,
        "compliance_flags": [],
        "insurance_general_liability_min": None,
        "insurance_auto_liability_min": None,
        "insurance_professional_liability_min": None,
        "workers_comp_required": None,
        "performance_bond_amount": None,
        "payment_bond_amount": None,
        "liquidated_damages_rate": None,
        "procurement_method": None,
        "cooperative_contract_ref": None,
        "prequalification_required": None,
        "raw_extraction": {},
        "extraction_confidence": 0.92,
        "source_highlights": [],
    }
    defaults.update(overrides)
    ef = MagicMock(spec=ExtractedFields)
    for k, v in defaults.items():
        setattr(ef, k, v)
    return ef


def _make_validation(doc_id, **overrides):
    """Create a mock ValidationResult."""
    defaults = {
        "id": uuid.uuid4(),
        "document_id": doc_id,
        "rule_code": "MISSING_AMOUNT",
        "severity": "warning",
        "field_name": "total_amount",
        "message": "Total amount is missing",
        "suggestion": "Add total amount",
        "resolved": False,
        "resolved_by": None,
        "resolved_at": None,
    }
    defaults.update(overrides)
    vr = MagicMock(spec=ValidationResult)
    for k, v in defaults.items():
        setattr(vr, k, v)
    return vr


def _make_doc(doc_id=None, with_fields=False, with_validations=False):
    """Create a mock Document with optional extracted fields and validations."""
    doc_id = doc_id or uuid.uuid4()
    now = datetime.now(timezone.utc)
    doc = MagicMock(spec=Document)
    doc.id = doc_id
    doc.filename = "test-contract.pdf"
    doc.original_filename = "test-contract.pdf"
    doc.source = "upload"
    doc.status = "extracted"
    doc.document_type = "contract"
    doc.submitted_by = None
    doc.approved_by = None
    doc.created_at = now
    doc.updated_at = now
    doc.blob_url = None
    doc.file_size_bytes = 12345
    doc.mime_type = "application/pdf"
    doc.page_count = 3
    doc.ocr_text = "sample text"
    doc.ocr_confidence = 0.95
    doc.classification_confidence = 0.88
    doc.error_message = None
    doc.submitted_at = None
    doc.approved_at = None
    doc.rejection_reason = None
    doc.processed_at = now
    doc.uploaded_at = now

    if with_fields:
        doc.extracted_fields = _make_extracted_fields(doc_id)
    else:
        doc.extracted_fields = None

    if with_validations:
        doc.validations = [_make_validation(doc_id)]
    else:
        doc.validations = []

    doc.activity = []
    return doc


def _make_mock_db(doc):
    """Create a mock AsyncSession that returns `doc` on select."""
    mock_db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = doc
    mock_db.execute = AsyncMock(return_value=result)
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    return mock_db


# ---------------------------------------------------------------------------
# Field Edit Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_field_edit_updates_extracted_fields(client):
    """PATCH /api/v1/documents/{id}/fields updates fields and returns schema."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, with_fields=True)
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.patch(
            f"/api/v1/documents/{doc_id}/fields",
            json={"updated_by": "analyst1", "fields": {"vendor_name": "New Vendor"}},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "document_id" in data
    # Activity log should have been added
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_field_edit_on_nonexistent_document_returns_404(client):
    """PATCH /api/v1/documents/{id}/fields returns 404 for missing document."""
    fake_id = uuid.uuid4()
    mock_db = _make_mock_db(None)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.patch(
            f"/api/v1/documents/{fake_id}/fields",
            json={"updated_by": "analyst1", "fields": {"vendor_name": "X"}},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_field_edit_no_extracted_fields_returns_404(client):
    """PATCH /api/v1/documents/{id}/fields returns 404 when no extracted fields exist."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, with_fields=False)
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.patch(
            f"/api/v1/documents/{doc_id}/fields",
            json={"updated_by": "analyst1", "fields": {"vendor_name": "X"}},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404
    assert "no extracted fields" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Review Endpoint Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_review_endpoint_updates_status_and_logs_activity(client):
    """POST /api/v1/documents/{id}/review marks document and creates activity."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id)
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/review",
            json={"reviewed_by": "analyst1", "role": "analyst", "notes": "Looks good"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(doc_id)
    # Activity log should have been added
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_review_nonexistent_document_returns_404(client):
    """POST /api/v1/documents/{id}/review returns 404 for missing document."""
    fake_id = uuid.uuid4()
    mock_db = _make_mock_db(None)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{fake_id}/review",
            json={"reviewed_by": "analyst1", "role": "analyst"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# CSV Export Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_csv_export_returns_text_csv(client):
    """GET /api/v1/documents/{id}/export/csv returns text/csv with headers."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, with_fields=True)
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get(f"/api/v1/documents/{doc_id}/export/csv")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "content-disposition" in response.headers
    assert "attachment" in response.headers["content-disposition"]
    # Verify CSV has header row and data row
    lines = response.text.strip().split("\n")
    assert len(lines) == 2
    assert "vendor_name" in lines[0]
    assert "total_amount" in lines[0]


@pytest.mark.asyncio
async def test_csv_export_no_fields_returns_404(client):
    """GET /api/v1/documents/{id}/export/csv returns 404 when no extracted fields."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, with_fields=False)
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get(f"/api/v1/documents/{doc_id}/export/csv")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Resolve Warning Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_warning_marks_validation_resolved(client):
    """POST /api/v1/documents/{id}/resolve-warning resolves the validation."""
    doc_id = uuid.uuid4()
    vr_id = uuid.uuid4()
    vr = _make_validation(doc_id, id=vr_id)

    mock_db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = vr
    mock_db.execute = AsyncMock(return_value=result)
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/resolve-warning",
            json={"validation_id": str(vr_id), "resolved_by": "analyst1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "rule_code" in data
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_warning_missing_fields_returns_400(client):
    """POST /api/v1/documents/{id}/resolve-warning returns 400 without required fields."""
    doc_id = uuid.uuid4()
    mock_db = AsyncMock()

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/resolve-warning",
            json={},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 400
    assert "required" in response.json()["detail"].lower()
