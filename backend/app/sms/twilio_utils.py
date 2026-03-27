from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from app.config import settings


def get_validator() -> RequestValidator:
    return RequestValidator(settings.twilio_auth_token)


def build_twiml_response(message: str) -> str:
    resp = MessagingResponse()
    resp.message(message)
    return str(resp)


def build_empty_twiml() -> str:
    return str(MessagingResponse())
