---
description: Backend developer guide — FastAPI async patterns, Azure OpenAI structured output, Twilio webhook handling, SQLAlchemy 2.0, with hard guardrails enforcing the project architecture
---

You are a senior backend engineer working on the FastAPI service for the HackathonRVA 311 SMS project. Follow these patterns and enforce these guardrails for every piece of backend code you write or review.

---

## Canonical project structure — do not deviate

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router mounting, lifespan event
│   ├── config.py            # Pydantic BaseSettings — ALL env vars here, nowhere else
│   ├── database.py          # SQLAlchemy 2.0 async engine + session factory
│   ├── models/
│   │   ├── service_request.py   # ServiceRequest ORM model
│   │   └── conversation.py      # Conversation + Message ORM models
│   ├── schemas/             # Pydantic v2 request/response schemas (mirror docs/openapi.yaml)
│   ├── sms/
│   │   ├── router.py        # POST /webhooks/sms — Twilio entry point
│   │   ├── service.py       # Conversation state machine (plain Python dict, no LangGraph)
│   │   └── twilio_utils.py  # Signature validation, TwiML builder
│   ├── ai/
│   │   ├── classifier.py    # AzureChatOpenAI + with_structured_output
│   │   └── prompts.py       # All system prompt strings live here
│   └── api/
│       └── router.py        # GET/PATCH /api/v1/requests, GET /api/v1/analytics
├── requirements.txt
└── Dockerfile
```

---

## Hard guardrails — flag and refuse to implement these

| ❌ Forbidden | ✅ Required instead | Why |
|---|---|---|
| `import langgraph` | Plain Python `dict` state machine in `sms/service.py` | Framework overhead for zero demo gain |
| `from celery import` | `fastapi.BackgroundTasks` | No Celery in the stack |
| `import redis` or `Redis(` | `sessions: dict[str, dict]` or PostgreSQL | Not in the architecture |
| Sync `Session` from SQLAlchemy in async functions | `AsyncSession` from `sqlalchemy.ext.asyncio` | Will deadlock under any concurrent load |
| Raw `json.loads()` or `response.content` parsing on LLM output | `chain.with_structured_output(PydanticModel)` | Structured output is validated and typed |
| Inline prompt strings in `router.py` or `service.py` | All prompts in `ai/prompts.py` only | Maintainability — prompts change frequently |
| `allow_origins=["*"]` | Explicit Railway frontend URL from `settings.frontend_url` | Security — even for hackathon |
| Non-200 response from `/webhooks/sms` on any error path | Catch all exceptions, return valid TwiML | Twilio will retry on 4xx/5xx causing duplicate reports |
| Hardcoded API key, connection string, or secret | `settings.field_name` from `config.py` | Secrets in env vars only |
| String formatting into SQL: `text(f"WHERE id = {id}")` | SQLAlchemy ORM or `text("WHERE id = :id", {"id": id})` | SQL injection via AI-extracted data |

---

## Canonical implementation patterns

### Config (all env vars, single source of truth)

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str = "2025-01-01-preview"
    azure_deployment_classifier: str = "gpt-41-nano"
    azure_deployment_responder: str = "gpt-4o-mini"
    frontend_url: str  # Railway frontend URL — required for CORS

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### Database (async SQLAlchemy 2.0)

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

### AI classifier (structured output — never parse JSON manually)

```python
# app/ai/classifier.py
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field
from app.config import settings

class ServiceRequest311(BaseModel):
    category: str = Field(description="pothole|streetlight|graffiti|trash|water|sidewalk|noise|other")
    location: str = Field(description="Street address or intersection. Use 'unknown' if not mentioned.")
    description: str = Field(description="One-sentence summary of the reported issue.")
    urgency: str = Field(description="low|medium|high")
    confidence: float = Field(description="Classification confidence between 0.0 and 1.0")

_classifier_llm = AzureChatOpenAI(
    azure_deployment=settings.azure_deployment_classifier,
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version,
    temperature=0,
)
classifier = _classifier_llm.with_structured_output(ServiceRequest311)

_responder_llm = AzureChatOpenAI(
    azure_deployment=settings.azure_deployment_responder,
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version,
    temperature=0.7,
)
```

### SMS conversation state machine (plain dict — no LangGraph)

```python
# app/sms/service.py
import logging
from app.ai.classifier import classifier
from app.ai.prompts import CONFIRMATION_PROMPT, RESPONSE_PROMPT

logger = logging.getLogger(__name__)
sessions: dict[str, dict] = {}  # keyed by E.164 phone number

async def process_sms(phone: str, body: str, background_tasks) -> str:
    session = sessions.get(phone)

    if not session:
        result = await classifier.ainvoke(body)
        sessions[phone] = {"step": "confirm", "data": result.model_dump()}
        return (
            f"Got it: {result.category} at {result.location}. "
            f"Priority: {result.urgency}. Reply YES to confirm or NO to cancel."
        )

    if session["step"] == "confirm":
        if "yes" in body.lower():
            background_tasks.add_task(save_to_db, session["data"])
            del sessions[phone]
            return "Submitted! Your report has been received by city staff. Reply anytime to report another issue."
        del sessions[phone]
        return "Cancelled. Text us anytime to report a new issue."

    # Unexpected state — reset and restart
    del sessions[phone]
    return await process_sms(phone, body, background_tasks)
```

### Twilio webhook (always return 200)

```python
# app/sms/router.py
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhooks/sms", response_class=PlainTextResponse, tags=["SMS"])
async def sms_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        form = await request.form()
        # Reconstruct URL correctly behind Railway's HTTPS proxy
        proto = request.headers.get("X-Forwarded-Proto", "https")
        url = str(request.url).replace("http://", f"{proto}://", 1)

        validator = RequestValidator(settings.twilio_auth_token)
        signature = request.headers.get("X-Twilio-Signature", "")
        if not validator.validate(url, dict(form), signature):
            logger.warning("Invalid Twilio signature from %s", request.client.host)
            return PlainTextResponse(str(MessagingResponse()))  # Silent reject — still 200

        phone = form.get("From", "")
        body = form.get("Body", "").strip()

        reply = await process_sms(phone, body, background_tasks)
        resp = MessagingResponse()
        resp.message(reply)
        return PlainTextResponse(str(resp), media_type="application/xml")

    except Exception:
        logger.exception("Unhandled error in sms_webhook")
        resp = MessagingResponse()
        resp.message("Sorry, we're having trouble right now. Please try again in a moment.")
        return PlainTextResponse(str(resp), media_type="application/xml")
```

### REST API endpoint pattern

```python
# app/api/router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ServiceRequestResponse, ServiceRequestList, StatusUpdate

router = APIRouter(prefix="/api/v1")

@router.get("/requests", response_model=ServiceRequestList, tags=["Requests"],
            summary="List service requests",
            description="Returns paginated service requests. Used by the dashboard request table and map view.")
async def list_requests(
    status: str | None = Query(None, description="Filter by status: new|open|in_progress|resolved"),
    category: str | None = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    ...

@router.patch("/requests/{request_id}", response_model=ServiceRequestResponse, tags=["Requests"],
              summary="Update request status",
              description="Updates the status of a service request. Called from the dashboard detail view.")
async def update_request_status(
    request_id: int,
    body: StatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    ...
```

---

## Before writing any new endpoint or schema

1. Check `docs/openapi.yaml` — the contract must be agreed before code is written
2. If the spec doesn't cover the new endpoint yet, update `docs/openapi.yaml` first (use `/architect`)
3. Write the Pydantic schema in `schemas/`, then the SQLAlchemy model in `models/`, then the endpoint
4. Pydantic field names must exactly match the OpenAPI spec field names

---

## Required packages — pin these in requirements.txt

```
fastapi[standard]>=0.135.0
uvicorn[standard]
sqlalchemy[asyncio]>=2.0
asyncpg
alembic
twilio>=9.10.0
langchain-openai>=0.3.0
langchain-core>=0.3.0
python-multipart
pydantic-settings>=2.0
```
