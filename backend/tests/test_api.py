"""Tests for all REST API endpoints in /api/v1/."""

from datetime import datetime, timezone

from app.models import Conversation, Message, ServiceRequest


# ──────────────────────────────────────────────
# GET /api/v1/requests
# ──────────────────────────────────────────────


async def test_list_requests_empty(client):
    resp = await client.get("/api/v1/requests")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["limit"] == 50
    assert data["offset"] == 0


async def test_list_requests_with_data(client, sample_requests):
    resp = await client.get("/api/v1/requests")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    # Most recent first
    refs = [item["reference_number"] for item in data["items"]]
    assert "RVA-2026-AAA001" in refs


async def test_list_requests_phone_masked(client, sample_requests):
    resp = await client.get("/api/v1/requests")
    data = resp.json()
    for item in data["items"]:
        assert item["phone"].endswith("****")
        assert "phone_number" not in item


async def test_list_requests_status_filter(client, sample_requests):
    resp = await client.get("/api/v1/requests", params={"status": "new"})
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "new"


async def test_list_requests_category_filter(client, sample_requests):
    resp = await client.get("/api/v1/requests", params={"category": "graffiti"})
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["category"] == "graffiti"


async def test_list_requests_filter_no_match(client, sample_requests):
    resp = await client.get("/api/v1/requests", params={"status": "nonexistent"})
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


async def test_list_requests_pagination(client, sample_requests):
    resp = await client.get("/api/v1/requests", params={"limit": 2, "offset": 0})
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0

    resp2 = await client.get("/api/v1/requests", params={"limit": 2, "offset": 2})
    data2 = resp2.json()
    assert data2["total"] == 3
    assert len(data2["items"]) == 1


# ──────────────────────────────────────────────
# GET /api/v1/requests/{id}
# ──────────────────────────────────────────────


async def test_get_request_found(client, sample_requests):
    sr_id = sample_requests[0].id
    resp = await client.get(f"/api/v1/requests/{sr_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["reference_number"] == "RVA-2026-AAA001"
    assert data["category"] == "pothole"
    assert data["phone"].endswith("****")
    assert "messages" in data


async def test_get_request_with_messages(client, sample_requests, db_session):
    sr = sample_requests[0]
    conv = Conversation(
        phone_number=sr.phone_number,
        service_request_id=sr.id,
        status="completed",
        current_step="done",
        context={"category": "pothole"},
    )
    db_session.add(conv)
    await db_session.flush()

    msg = Message(
        conversation_id=conv.id,
        direction="inbound",
        body="There's a pothole on Main St",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(msg)
    await db_session.commit()

    resp = await client.get(f"/api/v1/requests/{sr.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["messages"]) == 1
    assert data["messages"][0]["body"] == "There's a pothole on Main St"


async def test_get_request_not_found(client):
    resp = await client.get("/api/v1/requests/99999")
    assert resp.status_code == 404


# ──────────────────────────────────────────────
# GET /api/v1/analytics/summary
# ──────────────────────────────────────────────


async def test_analytics_summary_empty(client):
    resp = await client.get("/api/v1/analytics/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_requests"] == 0
    assert data["by_status"] == {}
    assert data["by_category"] == {}


async def test_analytics_summary_with_data(client, sample_requests):
    resp = await client.get("/api/v1/analytics/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_requests"] == 3
    assert data["by_status"]["new"] == 1
    assert data["by_status"]["in_progress"] == 1
    assert data["by_status"]["resolved"] == 1
    assert data["by_category"]["pothole"] == 1
    assert data["by_category"]["streetlight"] == 1
    assert data["by_category"]["graffiti"] == 1


# ──────────────────────────────────────────────
# GET /api/v1/analytics/trend
# ──────────────────────────────────────────────


async def test_analytics_trend_empty(client):
    resp = await client.get("/api/v1/analytics/trend", params={"days": 7})
    assert resp.status_code == 200
    data = resp.json()
    assert data["days"] == 7
    assert len(data["data"]) == 7
    assert all(point["count"] == 0 for point in data["data"])


async def test_analytics_trend_with_data(client, sample_requests):
    # Note: SQLite func.date() returns strings not date objects, so the
    # counts_by_day lookup won't match Python date keys. This test verifies
    # the endpoint works; exact count aggregation is tested against PostgreSQL.
    resp = await client.get("/api/v1/analytics/trend", params={"days": 7})
    assert resp.status_code == 200
    data = resp.json()
    assert data["days"] == 7
    assert len(data["data"]) == 7
    # Each data point has required fields
    for point in data["data"]:
        assert "date" in point
        assert "count" in point
        assert isinstance(point["count"], int)


async def test_analytics_trend_default_days(client):
    resp = await client.get("/api/v1/analytics/trend")
    assert resp.status_code == 200
    data = resp.json()
    assert data["days"] == 7
    assert len(data["data"]) == 7
