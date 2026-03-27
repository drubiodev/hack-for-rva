"""Tests for analytics and risks endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database import get_db
from app.main import app


def _make_analytics_db(total=5, by_type=None, by_status=None, by_source=None, total_value=100000.0, processed_today=2):
    """Create a mock DB that returns analytics data in the expected query order."""
    mock_db = AsyncMock()

    # The analytics endpoint executes 5 queries in order:
    # 1. total documents count
    # 2. by_type group
    # 3. by_status group
    # 4. by_source group
    # 5. total contract value
    # 6. processed today count
    results = []

    # 1. Total
    r1 = MagicMock()
    r1.scalar.return_value = total
    results.append(r1)

    # 2. By type
    r2 = MagicMock()
    r2.all.return_value = list((by_type or {"contract": 3, "invoice": 2}).items())
    results.append(r2)

    # 3. By status
    r3 = MagicMock()
    r3.all.return_value = list((by_status or {"extracted": 4, "approved": 1}).items())
    results.append(r3)

    # 4. By source
    r4 = MagicMock()
    r4.all.return_value = list((by_source or {"socrata": 3, "upload": 2}).items())
    results.append(r4)

    # 5. Total value
    r5 = MagicMock()
    r5.scalar.return_value = total_value
    results.append(r5)

    # 6. Processed today
    r6 = MagicMock()
    r6.scalar.return_value = processed_today
    results.append(r6)

    mock_db.execute = AsyncMock(side_effect=results)
    return mock_db


def _make_risks_db(rows=None):
    """Create a mock DB for the risks endpoint."""
    mock_db = AsyncMock()
    result = MagicMock()
    result.all.return_value = rows or []
    mock_db.execute = AsyncMock(return_value=result)
    return mock_db


def _make_activity_db(entries=None):
    """Create a mock DB for the activity endpoint."""
    mock_db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = entries or []
    mock_db.execute = AsyncMock(return_value=result)
    return mock_db


@pytest.mark.asyncio
async def test_analytics_summary_returns_correct_structure(client):
    """GET /api/v1/analytics/summary returns AnalyticsSummarySchema."""
    mock_db = _make_analytics_db()

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get("/api/v1/analytics/summary")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 5
    assert data["by_type"] == {"contract": 3, "invoice": 2}
    assert data["by_status"] == {"extracted": 4, "approved": 1}
    assert data["by_source"] == {"socrata": 3, "upload": 2}
    assert data["total_contract_value"] == 100000.0
    assert data["documents_processed_today"] == 2


@pytest.mark.asyncio
async def test_analytics_risks_returns_correct_structure(client):
    """GET /api/v1/analytics/risks returns RiskSummarySchema with empty list."""
    mock_db = _make_risks_db(rows=[])

    async def _override():
        return mock_db

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.get("/api/v1/analytics/risks")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert "expiring_contracts" in data
    assert "total_expiring_30" in data
    assert "total_expiring_60" in data
    assert "total_expiring_90" in data
    assert data["expiring_contracts"] == []
    assert data["total_expiring_30"] == 0


@pytest.mark.asyncio
async def test_activity_returns_items(client):
    """GET /api/v1/activity returns {items: [...]}."""
    mock_db = _make_activity_db(entries=[])

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
    assert data["items"] == []
