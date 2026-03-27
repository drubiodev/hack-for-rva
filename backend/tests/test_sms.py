"""Tests for the SMS state machine in app.sms.service."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.ai.classifier import ServiceRequest311
from app.models.service_request import ServiceRequest
from app.sms.service import process_sms, sessions


def _mock_classify_result(**overrides):
    defaults = {
        "category": "pothole",
        "location": "100 Main St",
        "description": "Large pothole in the road",
        "urgency": 4,
        "confidence": 0.95,
    }
    defaults.update(overrides)
    return ServiceRequest311(**defaults)


def _make_background_tasks():
    bt = MagicMock()
    bt.add_task = MagicMock()
    return bt


async def test_initial_message_triggers_classification(db_session):
    """First message from a phone number should classify and prompt for confirmation."""
    phone = "+18045551111"
    sessions.pop(phone, None)

    mock_result = _mock_classify_result()
    bt = _make_background_tasks()

    with patch("app.sms.service.classify_message", new_callable=AsyncMock, return_value=mock_result):
        reply = await process_sms(phone, "There's a big pothole on Main St", bt, db_session)

    assert "pothole" in reply
    assert "100 Main St" in reply
    assert "YES" in reply
    assert phone in sessions
    assert sessions[phone]["step"] == "confirm"

    # Cleanup
    sessions.pop(phone, None)


async def test_yes_confirmation_triggers_save(db_session):
    """Replying YES should submit the report and call save_to_db via background tasks."""
    phone = "+18045552222"
    sessions[phone] = {
        "step": "confirm",
        "data": _mock_classify_result().model_dump(),
        "original_body": "pothole on Main St",
        "twilio_sid": "SM123",
    }

    bt = _make_background_tasks()
    reply = await process_sms(phone, "YES", bt, db_session)

    assert "Submitted" in reply
    assert phone not in sessions
    bt.add_task.assert_called_once()


async def test_yes_variants_accepted(db_session):
    """Various affirmative responses should be accepted."""
    for word in ("yes", "y", "yeah", "yep", "confirm", "  YES  "):
        phone = "+18045553333"
        sessions[phone] = {
            "step": "confirm",
            "data": _mock_classify_result().model_dump(),
            "original_body": "test",
            "twilio_sid": None,
        }
        bt = _make_background_tasks()
        reply = await process_sms(phone, word, bt, db_session)
        assert "Submitted" in reply, f"Expected submission for '{word}'"
        assert phone not in sessions


async def test_no_cancels_session(db_session):
    """Replying NO (or anything other than yes) should cancel."""
    phone = "+18045554444"
    sessions[phone] = {
        "step": "confirm",
        "data": _mock_classify_result().model_dump(),
        "original_body": "test",
        "twilio_sid": None,
    }

    bt = _make_background_tasks()
    reply = await process_sms(phone, "NO", bt, db_session)

    assert "Cancelled" in reply
    assert phone not in sessions
    bt.add_task.assert_not_called()


async def test_cancel_clears_session(db_session):
    """Replying 'cancel' should clear the session."""
    phone = "+18045555555"
    sessions[phone] = {
        "step": "confirm",
        "data": _mock_classify_result().model_dump(),
        "original_body": "test",
        "twilio_sid": None,
    }

    bt = _make_background_tasks()
    reply = await process_sms(phone, "cancel", bt, db_session)

    assert "Cancelled" in reply
    assert phone not in sessions


async def test_new_message_after_cancel(db_session):
    """After cancelling, a new message should start fresh classification."""
    phone = "+18045556666"
    sessions.pop(phone, None)

    mock_result = _mock_classify_result(category="streetlight", location="200 Park Ave")
    bt = _make_background_tasks()

    with patch("app.sms.service.classify_message", new_callable=AsyncMock, return_value=mock_result):
        reply = await process_sms(phone, "Broken streetlight on Park Ave", bt, db_session)

    assert "streetlight" in reply
    assert "200 Park Ave" in reply
    assert phone in sessions

    sessions.pop(phone, None)


async def test_session_stores_correct_data(db_session):
    """Session should store classification data correctly."""
    phone = "+18045557777"
    sessions.pop(phone, None)

    mock_result = _mock_classify_result(
        category="graffiti",
        location="Bridge underpass",
        urgency=2,
    )
    bt = _make_background_tasks()

    with patch("app.sms.service.classify_message", new_callable=AsyncMock, return_value=mock_result):
        await process_sms(phone, "graffiti on the bridge", bt, db_session, twilio_sid="SM456")

    session = sessions[phone]
    assert session["data"]["category"] == "graffiti"
    assert session["data"]["location"] == "Bridge underpass"
    assert session["data"]["urgency"] == 2
    assert session["original_body"] == "graffiti on the bridge"
    assert session["twilio_sid"] == "SM456"

    sessions.pop(phone, None)


# ──────────────────────────────────────────────
# STATUS query tests
# ──────────────────────────────────────────────


async def test_status_query_with_existing_report(db_session):
    """STATUS should return the latest report for the phone number."""
    phone = "+18045558888"
    sr = ServiceRequest(
        reference_number="RVA-2026-TEST01",
        phone_number=phone,
        category="pothole",
        description="Big pothole",
        location="100 Main St",
        urgency=4,
        status="in_progress",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(sr)
    await db_session.commit()

    bt = _make_background_tasks()
    reply = await process_sms(phone, "STATUS", bt, db_session)

    assert "RVA-2026-TEST01" in reply
    assert "pothole" in reply
    assert "100 Main St" in reply
    assert "in_progress" in reply


async def test_status_query_case_insensitive(db_session):
    """STATUS query should work with any casing."""
    phone = "+18045559999"
    sr = ServiceRequest(
        reference_number="RVA-2026-TEST02",
        phone_number=phone,
        category="graffiti",
        description="Graffiti",
        location="200 Park Ave",
        urgency=2,
        status="new",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(sr)
    await db_session.commit()

    bt = _make_background_tasks()
    for word in ("status", "Status", "STATUS", "  status  "):
        reply = await process_sms(phone, word, bt, db_session)
        assert "RVA-2026-TEST02" in reply, f"STATUS not recognized for '{word}'"


async def test_status_query_no_reports(db_session):
    """STATUS with no prior reports should return a helpful message."""
    phone = "+18045550000"
    bt = _make_background_tasks()
    reply = await process_sms(phone, "STATUS", bt, db_session)

    assert "No reports found" in reply
