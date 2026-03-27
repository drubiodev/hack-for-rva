"""Tests for the /health endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_stub_endpoints_return_501(client):
    """Stub endpoints should return 501 Not Implemented."""
    response = await client.post("/api/v1/documents/upload")
    assert response.status_code in (501, 422)  # 422 if missing form data

    response = await client.get("/api/v1/analytics/summary")
    assert response.status_code == 501

    response = await client.get("/api/v1/analytics/risks")
    assert response.status_code == 501

    response = await client.get("/api/v1/activity")
    assert response.status_code == 501

    # Socrata ingest endpoint is now implemented — tested in test_socrata.py
