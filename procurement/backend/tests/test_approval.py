"""Tests for approval workflow endpoints: submit, approve, reject, reprocess."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.database import get_db
from app.main import app
from app.models.document import ActivityLog, Document, ExtractedFields


def _make_doc(doc_id=None, status="extracted", with_fields=False):
    """Create a mock Document."""
    doc_id = doc_id or uuid.uuid4()
    now = datetime.now(timezone.utc)
    doc = MagicMock(spec=Document)
    doc.id = doc_id
    doc.filename = "test-contract.pdf"
    doc.original_filename = "test-contract.pdf"
    doc.source = "upload"
    doc.status = status
    doc.document_type = "contract"
    doc.submitted_by = None
    doc.approved_by = None
    doc.created_at = now
    doc.updated_at = now
    doc.blob_url = "https://blob.example.com/test.pdf"
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
    doc.validations = []
    doc.activity = []

    if with_fields:
        ef = MagicMock(spec=ExtractedFields)
        ef.id = uuid.uuid4()
        ef.document_id = doc_id
        ef.vendor_name = "Acme Corp"
        ef.total_amount = 50000.0
        ef.expiration_date = None
        doc.extracted_fields = ef
    else:
        doc.extracted_fields = None

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
# Submit for Approval
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_submit_for_approval_valid(client):
    """POST /submit with valid status transitions to pending_approval."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, status="extracted")
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/submit",
            json={"submitted_by": "analyst1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(doc_id)
    assert doc.status == "pending_approval"
    assert doc.submitted_by == "analyst1"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_submit_for_approval_analyst_review_status(client):
    """POST /submit also works from analyst_review status."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, status="analyst_review")
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/submit",
            json={"submitted_by": "analyst1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert doc.status == "pending_approval"


@pytest.mark.asyncio
async def test_submit_wrong_status_returns_400(client):
    """POST /submit returns 400 if status is not extracted/analyst_review."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, status="uploading")
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/submit",
            json={"submitted_by": "analyst1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 400
    assert "uploading" in response.json()["detail"]


@pytest.mark.asyncio
async def test_submit_not_found_returns_404(client):
    """POST /submit returns 404 for missing document."""
    fake_id = uuid.uuid4()
    mock_db = _make_mock_db(None)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{fake_id}/submit",
            json={"submitted_by": "analyst1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Approve
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_approve_valid(client):
    """POST /approve with pending_approval status transitions to approved."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, status="pending_approval")
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/approve",
            json={"approved_by": "supervisor1", "comments": "Looks good"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert doc.status == "approved"
    assert doc.approved_by == "supervisor1"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_approve_wrong_status_returns_400(client):
    """POST /approve returns 400 if status is not pending_approval."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, status="extracted")
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/approve",
            json={"approved_by": "supervisor1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Reject
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reject_valid(client):
    """POST /reject with pending_approval status transitions to rejected."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, status="pending_approval")
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/reject",
            json={"rejected_by": "supervisor1", "reason": "Missing signatures"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert doc.status == "rejected"
    assert doc.rejection_reason == "Missing signatures"
    mock_db.add.assert_called_once()


@pytest.mark.asyncio
async def test_reject_without_reason_returns_422(client):
    """POST /reject without reason field returns 422 validation error."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, status="pending_approval")
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/reject",
            json={"rejected_by": "supervisor1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_reject_wrong_status_returns_400(client):
    """POST /reject returns 400 if status is not pending_approval."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, status="extracted")
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/reject",
            json={"rejected_by": "supervisor1", "reason": "Bad data"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Reprocess
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reprocess_triggers_background_task(client):
    """POST /reprocess resets status and triggers background pipeline."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, status="error")
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        with patch("app.pipeline.process_document") as mock_pipeline:
            response = await client.post(
                f"/api/v1/documents/{doc_id}/reprocess",
                json={"requested_by": "supervisor1"},
            )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 202
    assert doc.status == "uploading"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
