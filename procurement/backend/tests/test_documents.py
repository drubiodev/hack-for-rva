"""Tests for document list and detail endpoints."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.document import Document, ExtractedFields, ValidationResult


def _make_doc(**overrides):
    """Create a mock Document with sensible defaults."""
    doc_id = overrides.pop("id", uuid.uuid4())
    now = datetime.now(timezone.utc)
    defaults = {
        "id": doc_id,
        "filename": "test-contract.pdf",
        "original_filename": "test-contract.pdf",
        "source": "upload",
        "status": "extracted",
        "document_type": "contract",
        "submitted_by": None,
        "approved_by": None,
        "created_at": now,
        "updated_at": now,
        "blob_url": None,
        "file_size_bytes": 12345,
        "mime_type": "application/pdf",
        "page_count": 3,
        "ocr_text": "sample text",
        "ocr_confidence": 0.95,
        "classification_confidence": 0.88,
        "error_message": None,
        "submitted_at": None,
        "approved_at": None,
        "rejection_reason": None,
        "processed_at": now,
        "uploaded_at": now,
        "extracted_fields": None,
        "validations": [],
        "activity": [],
    }
    defaults.update(overrides)
    doc = MagicMock(spec=Document)
    for k, v in defaults.items():
        setattr(doc, k, v)
    return doc


def _make_mock_db(documents=None, single_doc=None):
    """Create a mock AsyncSession for document queries."""
    mock_db = AsyncMock()

    if documents is not None:
        # For list queries: first call returns count, second returns docs
        count_result = MagicMock()
        count_result.scalar.return_value = len(documents)

        docs_result = MagicMock()
        docs_result.scalars.return_value.all.return_value = documents

        mock_db.execute = AsyncMock(side_effect=[count_result, docs_result])
    elif single_doc is not None:
        result = MagicMock()
        result.scalar_one_or_none.return_value = single_doc
        mock_db.execute = AsyncMock(return_value=result)
    else:
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

    return mock_db


@pytest.mark.asyncio
async def test_list_documents_returns_paginated_response(client):
    """GET /api/v1/documents returns paginated DocumentListResponse."""
    docs = [_make_doc(filename=f"doc-{i}.pdf") for i in range(3)]
    mock_db = _make_mock_db(documents=docs)

    from app.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = await client.get("/api/v1/documents")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_list_documents_with_status_filter(client):
    """GET /api/v1/documents?status=extracted filters by status."""
    docs = [_make_doc(status="extracted")]
    mock_db = _make_mock_db(documents=docs)

    from app.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = await client.get("/api/v1/documents?status=extracted")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "extracted"


@pytest.mark.asyncio
async def test_list_documents_with_source_filter(client):
    """GET /api/v1/documents?source=socrata filters by source."""
    docs = [_make_doc(source="socrata")]
    mock_db = _make_mock_db(documents=docs)

    from app.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = await client.get("/api/v1/documents?source=socrata")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["source"] == "socrata"


@pytest.mark.asyncio
async def test_list_documents_with_search_filter(client):
    """GET /api/v1/documents?search=acme filters by filename."""
    docs = [_make_doc(filename="acme-contract.pdf", original_filename="acme-contract.pdf")]
    mock_db = _make_mock_db(documents=docs)

    from app.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = await client.get("/api/v1/documents?search=acme")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_document_detail_existing(client):
    """GET /api/v1/documents/{id} returns full detail for existing document."""
    doc_id = uuid.uuid4()
    doc = _make_doc(id=doc_id)
    mock_db = _make_mock_db(single_doc=doc)

    from app.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = await client.get(f"/api/v1/documents/{doc_id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(doc_id)
    assert data["filename"] == "test-contract.pdf"
    assert data["status"] == "extracted"
    # Detail-only fields present
    assert "ocr_text" in data
    assert "validations" in data
    assert "activity" in data


@pytest.mark.asyncio
async def test_get_document_detail_not_found(client):
    """GET /api/v1/documents/{id} returns 404 for non-existent document."""
    fake_id = uuid.uuid4()
    mock_db = _make_mock_db(single_doc=None)

    from app.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = await client.get(f"/api/v1/documents/{fake_id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


@pytest.mark.asyncio
async def test_list_documents_empty(client):
    """GET /api/v1/documents returns empty list when no documents exist."""
    mock_db = _make_mock_db(documents=[])

    from app.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = await client.get("/api/v1/documents")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["total_pages"] == 1
