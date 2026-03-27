import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.classifier import classify_message
from app.database import AsyncSessionLocal
from app.models.conversation import Conversation, Message
from app.models.service_request import ServiceRequest

logger = logging.getLogger(__name__)

sessions: dict[str, dict] = {}


def _generate_reference_number() -> str:
    year = datetime.now(timezone.utc).year
    short_id = uuid.uuid4().hex[:6].upper()
    return f"RVA-{year}-{short_id}"


async def save_to_db(
    phone: str,
    data: dict,
    inbound_body: str,
    reply_body: str,
    twilio_sid: str | None,
) -> None:
    try:
        async with AsyncSessionLocal() as db:
            ref = _generate_reference_number()
            sr = ServiceRequest(
                reference_number=ref,
                phone_number=phone,
                category=data["category"],
                description=data["description"],
                location=data["location"],
                urgency=data["urgency"],
                status="new",
            )
            db.add(sr)
            await db.flush()

            conv = Conversation(
                phone_number=phone,
                service_request_id=sr.id,
                status="completed",
                current_step="done",
                context=data,
            )
            db.add(conv)
            await db.flush()

            inbound_msg = Message(
                conversation_id=conv.id,
                direction="inbound",
                body=inbound_body,
                twilio_sid=twilio_sid,
            )
            outbound_msg = Message(
                conversation_id=conv.id,
                direction="outbound",
                body=reply_body,
            )
            db.add(inbound_msg)
            db.add(outbound_msg)

            await db.commit()
            logger.info("Saved service request %s for %s", ref, phone)
    except Exception:
        logger.exception("Failed to save service request to database")


async def process_sms(
    phone: str,
    body: str,
    background_tasks: object,
    db: AsyncSession,
    twilio_sid: str | None = None,
) -> str:
    session = sessions.get(phone)

    if not session:
        result = await classify_message(body)
        data = result.model_dump()
        sessions[phone] = {
            "step": "confirm",
            "data": data,
            "original_body": body,
            "twilio_sid": twilio_sid,
        }
        return (
            f"Got it: {result.category} at {result.location}. "
            f"Urgency: {result.urgency}/5. "
            f"Reply YES to confirm or NO to cancel."
        )

    if session["step"] == "confirm":
        if body.strip().lower() in ("yes", "y", "yeah", "yep", "confirm"):
            reply = (
                "Submitted! Your report has been received by city staff. "
                "Reply anytime to report another issue."
            )
            background_tasks.add_task(
                save_to_db,
                phone,
                session["data"],
                session["original_body"],
                reply,
                session.get("twilio_sid"),
            )
            del sessions[phone]
            return reply
        del sessions[phone]
        return "Cancelled. Text us anytime to report a new issue."

    del sessions[phone]
    return await process_sms(phone, body, background_tasks, db, twilio_sid)
