"""Tests for the chat endpoint: POST /api/v1/chat."""

import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database import get_db
from app.main import app
from app.models.document import Document, ExtractedFields


@pytest.mark.asyncio
async def test_chat_with_question_returns_response(client):
    """POST /chat with a question returns answer, sources, and conversation_id."""
    doc_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    doc = MagicMock(spec=Document)
    doc.id = doc_id
    doc.filename = "contract-acme.pdf"
    doc.ocr_text = "acme corporation contract for maintenance services"

    ef = MagicMock(spec=ExtractedFields)
    ef.title = "Acme Maintenance Contract"
    ef.vendor_name = "Acme Corp"
    ef.total_amount = 75000.0
    ef.expiration_date = date.today()

    mock_db = AsyncMock()
    result_mock = MagicMock()
    result_mock.all.return_value = [(doc, ef)]
    mock_db.execute = AsyncMock(return_value=result_mock)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            "/api/v1/chat",
            json={"question": "What contracts does Acme have?"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "conversation_id" in data
    assert len(data["sources"]) == 1
    assert data["sources"][0]["document_id"] == str(doc_id)


@pytest.mark.asyncio
async def test_chat_with_empty_question_returns_response(client):
    """POST /chat with empty/short words returns a helpful message."""
    mock_db = AsyncMock()

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            "/api/v1/chat",
            json={"question": "hi"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "conversation_id" in data
    # With the query router, "hi" is classified as general_knowledge and gets an AI response
    assert len(data["answer"]) > 0


@pytest.mark.asyncio
async def test_chat_no_matches_returns_empty_sources(client):
    """POST /chat with no matching documents returns empty sources."""
    mock_db = AsyncMock()
    result_mock = MagicMock()
    result_mock.all.return_value = []
    mock_db.execute = AsyncMock(return_value=result_mock)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            "/api/v1/chat",
            json={"question": "xyznonexistent vendor contracts"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["sources"] == []
    assert "no documents" in data["answer"].lower()


@pytest.mark.asyncio
async def test_chat_with_conversation_id_preserves_it(client):
    """POST /chat with a conversation_id returns the same conversation_id."""
    conv_id = str(uuid.uuid4())

    mock_db = AsyncMock()
    result_mock = MagicMock()
    result_mock.all.return_value = []
    mock_db.execute = AsyncMock(return_value=result_mock)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            "/api/v1/chat",
            json={"question": "maintenance contracts renewal", "conversation_id": conv_id},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == conv_id
