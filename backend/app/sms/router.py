import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.sms.service import process_sms
from app.sms.twilio_utils import build_empty_twiml, build_twiml_response, get_validator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhooks/sms", tags=["SMS"])
async def sms_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Response:
    try:
        form = await request.form()

        if settings.environment != "development":
            proto = request.headers.get("X-Forwarded-Proto", "https")
            url = str(request.url).replace("http://", f"{proto}://", 1)
            validator = get_validator()
            signature = request.headers.get("X-Twilio-Signature", "")
            if not validator.validate(url, dict(form), signature):
                logger.warning("Invalid Twilio signature from %s", request.client.host)
                return Response(
                    content=build_empty_twiml(),
                    media_type="application/xml",
                    status_code=200,
                )

        phone = form.get("From", "")
        body = form.get("Body", "").strip()
        twilio_sid = form.get("MessageSid")

        reply = await process_sms(phone, body, background_tasks, db, twilio_sid)

        return Response(
            content=build_twiml_response(reply),
            media_type="application/xml",
            status_code=200,
        )

    except Exception:
        logger.exception("Unhandled error in sms_webhook")
        return Response(
            content=build_twiml_response(
                "Sorry, we're having trouble right now. Please try again in a moment."
            ),
            media_type="application/xml",
            status_code=200,
        )
