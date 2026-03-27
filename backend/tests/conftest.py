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
    "FRONTEND_URL": "http://localhost:3000",
}
for key, val in _DUMMY_VARS.items():
    os.environ.setdefault(key, val)

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
