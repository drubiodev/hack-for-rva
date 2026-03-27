"""Test fixtures for the procurement backend."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """Async HTTP client that talks directly to the FastAPI app.

    Patches init_db to skip real DB connection — tests that need DB
    should override the get_db dependency instead.
    """
    with patch("app.main.init_db", new_callable=AsyncMock):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
