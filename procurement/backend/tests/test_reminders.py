"""Tests for reminder endpoints: create, list, dismiss, and risk integration."""

import uuid
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database import get_db
from app.main import app
from app.models.document import ContractReminder, Document, ExtractedFields


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
    doc.validations = []
    doc.activity = []
    doc.reminders = []

    if with_fields:
        ef = MagicMock(spec=ExtractedFields)
        ef.id = uuid.uuid4()
        ef.document_id = doc_id
        ef.vendor_name = "Acme Corp"
        ef.total_amount = 50000.0
        ef.expiration_date = date.today() + timedelta(days=60)
        ef.title = "Test Contract"
        doc.extracted_fields = ef
    else:
        doc.extracted_fields = None

    return doc


def _make_reminder(reminder_id=None, document_id=None, status="pending", reminder_date=None):
    """Create a mock ContractReminder."""
    reminder_id = reminder_id or uuid.uuid4()
    document_id = document_id or uuid.uuid4()
    now = datetime.now(timezone.utc)
    rem = MagicMock(spec=ContractReminder)
    rem.id = reminder_id
    rem.document_id = document_id
    rem.reminder_date = reminder_date or (date.today() + timedelta(days=7))
    rem.created_by = "analyst1"
    rem.note = "Follow up on renewal"
    rem.status = status
    rem.created_at = now
    rem.triggered_at = None
    return rem


# ---------------------------------------------------------------------------
# Create Reminder
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_reminder_valid(client):
    """POST /documents/{id}/reminders with valid body returns 201."""
    doc_id = uuid.uuid4()
    doc = _make_doc(doc_id=doc_id, with_fields=True)

    mock_db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = doc
    mock_db.execute = AsyncMock(return_value=result_mock)
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    reminder_date = (date.today() + timedelta(days=14)).isoformat()

    # After commit, refresh should populate the reminder fields
    async def fake_refresh(obj):
        if isinstance(obj, ContractReminder) or hasattr(obj, "reminder_date"):
            obj.id = uuid.uuid4()
            obj.created_at = datetime.now(timezone.utc)
            obj.triggered_at = None

    mock_db.refresh = AsyncMock(side_effect=fake_refresh)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{doc_id}/reminders",
            json={
                "reminder_date": reminder_date,
                "created_by": "analyst1",
                "note": "Renew soon",
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 201
    data = response.json()
    assert data["document_id"] == str(doc_id)
    assert data["status"] == "pending"
    assert data["created_by"] == "analyst1"
    assert data["note"] == "Renew soon"
    assert data["vendor_name"] == "Acme Corp"
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_reminder_missing_doc_returns_404(client):
    """POST /documents/{id}/reminders with fake UUID returns 404."""
    fake_id = uuid.uuid4()
    mock_db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=result_mock)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            f"/api/v1/documents/{fake_id}/reminders",
            json={
                "reminder_date": date.today().isoformat(),
                "created_by": "analyst1",
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# List Reminders
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_reminders_returns_items(client):
    """GET /reminders returns items list."""
    doc_id = uuid.uuid4()
    rem = _make_reminder(document_id=doc_id)

    ef = MagicMock(spec=ExtractedFields)
    ef.vendor_name = "Acme Corp"
    ef.title = "Test Contract"
    ef.expiration_date = date.today() + timedelta(days=60)

    mock_db = AsyncMock()
    result_mock = MagicMock()
    result_mock.all.return_value = [(rem, ef)]
    mock_db.execute = AsyncMock(return_value=result_mock)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get("/api/v1/reminders")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["vendor_name"] == "Acme Corp"


@pytest.mark.asyncio
async def test_list_reminders_with_status_filter(client):
    """GET /reminders?status=pending filters correctly."""
    doc_id = uuid.uuid4()
    rem = _make_reminder(document_id=doc_id, status="pending")

    ef = MagicMock(spec=ExtractedFields)
    ef.vendor_name = "Acme Corp"
    ef.title = "Test"
    ef.expiration_date = None

    mock_db = AsyncMock()
    result_mock = MagicMock()
    result_mock.all.return_value = [(rem, ef)]
    mock_db.execute = AsyncMock(return_value=result_mock)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get("/api/v1/reminders?status=pending")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "pending"


# ---------------------------------------------------------------------------
# Dismiss Reminder
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dismiss_reminder_valid(client):
    """PATCH /reminders/{id} with status=dismissed returns 200."""
    rem_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    rem = _make_reminder(reminder_id=rem_id, document_id=doc_id, status="triggered")

    ef = MagicMock(spec=ExtractedFields)
    ef.vendor_name = "Acme Corp"
    ef.title = "Test"
    ef.expiration_date = None

    mock_db = AsyncMock()
    # First call: select reminder; second call: select extracted fields
    reminder_result = MagicMock()
    reminder_result.scalar_one_or_none.return_value = rem

    ef_result = MagicMock()
    ef_result.scalar_one_or_none.return_value = ef

    mock_db.execute = AsyncMock(side_effect=[reminder_result, ef_result])
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.patch(
            f"/api/v1/reminders/{rem_id}",
            json={"status": "dismissed", "dismissed_by": "analyst1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert rem.status == "dismissed"
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_dismiss_nonexistent_reminder_returns_404(client):
    """PATCH /reminders/{id} with fake UUID returns 404."""
    fake_id = uuid.uuid4()
    mock_db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=result_mock)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.patch(
            f"/api/v1/reminders/{fake_id}",
            json={"status": "dismissed", "dismissed_by": "analyst1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Risk endpoint integration with reminders
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_risk_endpoint_includes_triggered_reminders(client):
    """GET /analytics/risks includes triggered_reminders in response."""
    rem_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    rem = MagicMock(spec=ContractReminder)
    rem.id = rem_id
    rem.document_id = doc_id
    rem.reminder_date = date.today()
    rem.created_by = "analyst1"
    rem.note = "Check renewal"
    rem.status = "triggered"
    rem.created_at = now
    rem.triggered_at = now

    ef = MagicMock(spec=ExtractedFields)
    ef.vendor_name = "Acme Corp"
    ef.title = "Test Contract"
    ef.expiration_date = date.today() + timedelta(days=30)

    mock_db = AsyncMock()
    call_count = 0

    async def multi_execute(stmt, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        result = MagicMock()
        if call_count == 1:
            # Expiring contracts query
            result.all.return_value = []
        elif call_count == 2:
            # Due reminders query (pending reminders due today)
            result.scalars.return_value.all.return_value = []
        elif call_count == 3:
            # Triggered reminders query
            result.all.return_value = [(rem, ef)]
        elif call_count == 4:
            # Pending count
            result.scalar.return_value = 0
        return result

    mock_db.execute = AsyncMock(side_effect=multi_execute)
    mock_db.commit = AsyncMock()

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get("/api/v1/analytics/risks")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert "triggered_reminders" in data
    assert len(data["triggered_reminders"]) == 1
    assert data["triggered_reminders"][0]["vendor_name"] == "Acme Corp"
    assert data["triggered_reminders"][0]["status"] == "triggered"


@pytest.mark.asyncio
async def test_risk_endpoint_includes_pending_reminders_count(client):
    """GET /analytics/risks includes pending_reminders_count > 0."""
    mock_db = AsyncMock()
    call_count = 0

    async def multi_execute(stmt, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        result = MagicMock()
        if call_count == 1:
            # Expiring contracts
            result.all.return_value = []
        elif call_count == 2:
            # Due reminders
            result.scalars.return_value.all.return_value = []
        elif call_count == 3:
            # Triggered reminders
            result.all.return_value = []
        elif call_count == 4:
            # Pending count
            result.scalar.return_value = 3
        return result

    mock_db.execute = AsyncMock(side_effect=multi_execute)
    mock_db.commit = AsyncMock()

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get("/api/v1/analytics/risks")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["pending_reminders_count"] == 3
