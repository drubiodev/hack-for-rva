"""Integration tests for analytics, risks, and activity endpoints with real data shapes."""

import uuid
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database import get_db
from app.main import app
from app.models.document import ActivityLog, Document, ExtractedFields


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_analytics_db(
    total=10,
    by_type=None,
    by_status=None,
    by_source=None,
    total_value=500000.0,
    processed_today=5,
):
    """Create a mock DB for analytics summary with realistic data."""
    mock_db = AsyncMock()
    results = []

    r1 = MagicMock()
    r1.scalar.return_value = total
    results.append(r1)

    r2 = MagicMock()
    r2.all.return_value = list(
        (by_type or {"contract": 5, "invoice": 3, "rfp": 2}).items()
    )
    results.append(r2)

    r3 = MagicMock()
    r3.all.return_value = list(
        (by_status or {"extracted": 6, "approved": 3, "error": 1}).items()
    )
    results.append(r3)

    r4 = MagicMock()
    r4.all.return_value = list(
        (by_source or {"socrata": 7, "upload": 3}).items()
    )
    results.append(r4)

    r5 = MagicMock()
    r5.scalar.return_value = total_value
    results.append(r5)

    r6 = MagicMock()
    r6.scalar.return_value = processed_today
    results.append(r6)

    mock_db.execute = AsyncMock(side_effect=results)
    return mock_db


def _make_expiring_contract(doc_id=None, days_until=20, vendor="Acme Corp", amount=100000.0):
    """Create a mock (Document, ExtractedFields) pair for risks endpoint."""
    doc_id = doc_id or uuid.uuid4()
    doc = MagicMock(spec=Document)
    doc.id = doc_id

    ef = MagicMock(spec=ExtractedFields)
    ef.vendor_name = vendor
    ef.title = f"Contract with {vendor}"
    ef.total_amount = amount
    ef.expiration_date = date.today() + timedelta(days=days_until)

    return (doc, ef)


def _make_activity_entry(doc_id=None, action="uploaded", actor="analyst1"):
    """Create a mock ActivityLog entry."""
    entry = MagicMock(spec=ActivityLog)
    entry.id = uuid.uuid4()
    entry.document_id = doc_id or uuid.uuid4()
    entry.action = action
    entry.actor_name = actor
    entry.actor_role = "analyst"
    entry.details = {}
    entry.created_at = datetime.now(timezone.utc)
    return entry


# ---------------------------------------------------------------------------
# Analytics Summary — with real data shapes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analytics_summary_with_real_data_shape(client):
    """Analytics summary returns all required fields with non-trivial data."""
    mock_db = _make_analytics_db(
        total=10,
        by_type={"contract": 5, "invoice": 3, "rfp": 2},
        by_status={"extracted": 6, "approved": 3, "error": 1},
        by_source={"socrata": 7, "upload": 3},
        total_value=500000.0,
        processed_today=5,
    )

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get("/api/v1/analytics/summary")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 10
    assert data["total_contract_value"] == 500000.0
    assert data["documents_processed_today"] == 5
    assert "contract" in data["by_type"]
    assert "socrata" in data["by_source"]
    # Verify all breakdown counts sum correctly
    assert sum(data["by_type"].values()) == 10
    assert sum(data["by_status"].values()) == 10
    assert sum(data["by_source"].values()) == 10


# ---------------------------------------------------------------------------
# Risks — with expiring contracts
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_risks_returns_expiring_contracts(client):
    """Risks endpoint returns contracts expiring within the window."""
    contracts = [
        _make_expiring_contract(days_until=15, vendor="Vendor A", amount=50000.0),
        _make_expiring_contract(days_until=45, vendor="Vendor B", amount=75000.0),
        _make_expiring_contract(days_until=80, vendor="Vendor C", amount=120000.0),
    ]

    mock_db = AsyncMock()
    result = MagicMock()
    result.all.return_value = contracts
    mock_db.execute = AsyncMock(return_value=result)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get("/api/v1/analytics/risks?days=90")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data["expiring_contracts"]) == 3
    assert data["total_expiring_30"] == 1  # only Vendor A (15 days)
    assert data["total_expiring_60"] == 2  # Vendor A + B
    assert data["total_expiring_90"] == 3  # all three
    # Verify structure of first contract
    first = data["expiring_contracts"][0]
    assert "vendor_name" in first
    assert "expiration_date" in first
    assert "days_until_expiry" in first
    assert first["vendor_name"] == "Vendor A"


# ---------------------------------------------------------------------------
# Activity — with entries
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_activity_returns_list_of_entries(client):
    """Activity endpoint returns a list of activity log entries."""
    entries = [
        _make_activity_entry(action="uploaded", actor="analyst1"),
        _make_activity_entry(action="field_edited", actor="analyst2"),
        _make_activity_entry(action="submitted", actor="analyst1"),
    ]

    mock_db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = entries
    mock_db.execute = AsyncMock(return_value=result)

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get("/api/v1/activity")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 3
    # Verify structure
    item = data["items"][0]
    assert "id" in item
    assert "document_id" in item
    assert "action" in item
    assert "actor_name" in item
    assert "actor_role" in item
    assert "created_at" in item
