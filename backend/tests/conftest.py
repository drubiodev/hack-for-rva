import os

# Set dummy env vars before importing the app, so pydantic-settings doesn't
# raise validation errors during tests.  Real values are NOT needed for unit
# tests that don't touch external services.
_DUMMY_VARS = {
    "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/test",
    "AZURE_OPENAI_ENDPOINT": "https://dummy.openai.azure.com",
    "AZURE_OPENAI_API_KEY": "dummy-key",
    "TWILIO_ACCOUNT_SID": "ACdummy",
    "TWILIO_AUTH_TOKEN": "dummy-token",
    "TWILIO_PHONE_NUMBER": "+10000000000",
    "FRONTEND_URL": "",
}
for key, val in _DUMMY_VARS.items():
    os.environ.setdefault(key, val)

import json

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import JSON, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models import Conversation, Message, ServiceRequest

# ---------- In-memory SQLite async engine for tests ----------

# Replace JSONB with JSON for SQLite compatibility
from app.models.conversation import Conversation as _Conv

_Conv.__table__.c.context.type = JSON()

TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


@event.listens_for(test_engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


# ---------- Fixtures ----------


@pytest_asyncio.fixture(autouse=True)
async def _setup_db():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Provide a test database session."""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """HTTP test client with DB dependency overridden to use test SQLite."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_requests(db_session):
    """Insert sample service requests and return them."""
    from datetime import datetime, timezone

    requests = []
    data = [
        ("RVA-2026-AAA001", "+18045551234", "pothole", "Large pothole on Main St", "100 Main St", 37.5407, -77.4360, 4, "new"),
        ("RVA-2026-AAA002", "+18045555678", "streetlight", "Broken streetlight near park", "200 Park Ave", 37.5500, -77.4500, 3, "in_progress"),
        ("RVA-2026-AAA003", "+18045559012", "graffiti", "Graffiti on bridge underpass", "I-95 overpass at Broad St", 37.5450, -77.4400, 2, "resolved"),
    ]
    for ref, phone, cat, desc, loc, lat, lng, urg, status in data:
        sr = ServiceRequest(
            reference_number=ref,
            phone_number=phone,
            category=cat,
            description=desc,
            location=loc,
            latitude=lat,
            longitude=lng,
            urgency=urg,
            status=status,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(sr)
        requests.append(sr)

    await db_session.commit()
    for sr in requests:
        await db_session.refresh(sr)
    return requests
