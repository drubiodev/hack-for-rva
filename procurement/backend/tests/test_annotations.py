"""Tests for document annotations and file endpoints."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database import get_db
from app.main import app
from app.models.document import ActivityLog, Document


def _make_doc(doc_id=None, with_annotations=False, with_blob_url=False):
    """Create a mock Document with optional annotations and blob_url."""
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
    doc.extracted_fields = None
    doc.validations = []
    doc.activity = []

    if with_annotations:
        doc.annotations = [
            {
                "id": "ann_123",
                "x": 50.0,
                "y": 25.0,
                "page": 1,
                "text": "test note",
                "author": "Analyst",
                "initials": "A",
                "time": "2026-03-28T12:00:00Z",
            }
        ]
    else:
        doc.annotations = []

    if with_blob_url:
        doc.blob_url = "https://example.blob.core.windows.net/docs/test.pdf"
    else:
        doc.blob_url = None

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
# GET /api/v1/documents/{id}/annotations
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_annotations_returns_list(client):
    """GET annotations on doc with annotations returns them."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, with_annotations=True)
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get(f"/api/v1/documents/{doc_id}/annotations")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "ann_123"
    assert data[0]["text"] == "test note"
    assert data[0]["x"] == 50.0
    assert data[0]["y"] == 25.0


@pytest.mark.asyncio
async def test_get_annotations_empty(client):
    """GET annotations on doc with no annotations returns empty list."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, with_annotations=False)
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get(f"/api/v1/documents/{doc_id}/annotations")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_get_annotations_not_found(client):
    """GET annotations on missing doc returns 404."""
    fake_id = uuid.uuid4()
    mock_db = _make_mock_db(None)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get(f"/api/v1/documents/{fake_id}/annotations")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/documents/{id}/annotations
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_annotation_success(client):
    """POST creates annotation, returns it with generated id/time."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, with_annotations=False)
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/annotations",
            json={
                "x": 100.0,
                "y": 200.0,
                "page": 2,
                "text": "Important clause",
                "author": "Jane Analyst",
                "initials": "JA",
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 201
    data = response.json()
    assert data["id"].startswith("ann_")
    assert data["x"] == 100.0
    assert data["y"] == 200.0
    assert data["page"] == 2
    assert data["text"] == "Important clause"
    assert data["author"] == "Jane Analyst"
    assert data["initials"] == "JA"
    assert "time" in data
    # Activity log should have been added
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_annotation_not_found(client):
    """POST on missing doc returns 404."""
    fake_id = uuid.uuid4()
    mock_db = _make_mock_db(None)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{fake_id}/annotations",
            json={
                "x": 10.0,
                "y": 20.0,
                "page": 1,
                "text": "note",
                "author": "Test",
                "initials": "T",
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/documents/{id}/file
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_file_with_blob_url(client):
    """GET file on doc with blob_url returns redirect (307)."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, with_blob_url=True)
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get(
            f"/api/v1/documents/{doc_id}/file",
            follow_redirects=False,
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.blob.core.windows.net/docs/test.pdf"


@pytest.mark.asyncio
async def test_get_file_no_blob_url(client):
    """GET file on doc without blob_url returns 404."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, with_blob_url=False)
    mock_db = _make_mock_db(doc)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get(f"/api/v1/documents/{doc_id}/file")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404
    assert "no file" in response.json()["detail"].lower()
