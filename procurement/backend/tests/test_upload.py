"""Tests for the document upload endpoint."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.database import get_db
from app.main import app
from app.models.document import Document


def _make_mock_db():
    """Create a mock AsyncSession for upload tests.

    Simulates server_default behavior: on flush, sets id and timestamps
    on any Document objects that were added.
    """
    mock_db = AsyncMock()
    added_objects: list = []

    def _track_add(obj):
        added_objects.append(obj)

    mock_db.add = MagicMock(side_effect=_track_add)

    async def _flush():
        for obj in added_objects:
            if isinstance(obj, Document):
                if obj.id is None:
                    obj.id = uuid.uuid4()
                if obj.created_at is None:
                    obj.created_at = datetime.now(timezone.utc)
                if obj.updated_at is None:
                    obj.updated_at = datetime.now(timezone.utc)
                if obj.uploaded_at is None:
                    obj.uploaded_at = datetime.now(timezone.utc)

    mock_db.flush = AsyncMock(side_effect=_flush)
    mock_db.commit = AsyncMock()

    # Configure execute to return a result where scalar_one_or_none() returns None
    # (no duplicate found for file hash check)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    return mock_db


@pytest.fixture
def override_db():
    """Override get_db with a mock and clean up after."""
    mock_db = _make_mock_db()

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    yield mock_db
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_upload_accepts_pdf_file(client, override_db):
    """Upload accepts a PDF file and returns 202."""
    pdf_content = b"%PDF-1.4 test content"
    files = {"file": ("contract.pdf", pdf_content, "application/pdf")}
    data = {"uploaded_by": "analyst1"}
    response = await client.post("/api/v1/documents/upload", files=files, data=data)
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "uploading"
    assert body["source"] == "upload"
    assert body["submitted_by"] == "analyst1"


@pytest.mark.asyncio
async def test_upload_rejects_exe_file(client, override_db):
    """Upload rejects .exe file with 400."""
    files = {"file": ("malware.exe", b"MZ\x90\x00", "application/octet-stream")}
    data = {"uploaded_by": "analyst1"}
    response = await client.post("/api/v1/documents/upload", files=files, data=data)
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_rejects_oversized_file(client, override_db):
    """Upload rejects files > 20MB with 400."""
    large_content = b"%PDF-1.4 " + b"x" * (21 * 1024 * 1024)
    files = {"file": ("huge.pdf", large_content, "application/pdf")}
    data = {"uploaded_by": "analyst1"}
    response = await client.post("/api/v1/documents/upload", files=files, data=data)
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_returns_document_summary(client, override_db):
    """Upload returns DocumentSummary with status=uploading and source=upload."""
    pdf_content = b"%PDF-1.4 test"
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    data = {"uploaded_by": "analyst1"}
    response = await client.post("/api/v1/documents/upload", files=files, data=data)
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "uploading"
    assert body["source"] == "upload"
    assert "id" in body
    assert "filename" in body
    assert "created_at" in body
