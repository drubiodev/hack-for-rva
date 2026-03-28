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
async def test_approval_endpoints_require_body(client):
    """Approval endpoints require a JSON body (422 without one)."""
    from uuid import uuid4

    fake_id = uuid4()

    response = await client.post(f"/api/v1/documents/{fake_id}/submit")
    assert response.status_code == 422

    response = await client.post(f"/api/v1/documents/{fake_id}/approve")
    assert response.status_code == 422

    response = await client.post(f"/api/v1/documents/{fake_id}/reject")
    assert response.status_code == 422

    response = await client.post(f"/api/v1/documents/{fake_id}/reprocess")
    assert response.status_code == 422
