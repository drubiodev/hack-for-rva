"""Tests for the Socrata CSV ingest endpoint."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.api.ingest import _parse_amount, _parse_csv_rows, _parse_date

# ---------------------------------------------------------------------------
# Sample CSV for mocking the download
# ---------------------------------------------------------------------------

SAMPLE_CSV = """Contract Number,Vendor Name,Department,Contract Amount,Start Date,End Date,Contract Type,Description
C-1001,Acme Corp,Public Works,$150000.00,01/15/2024,01/14/2026,Services,Road maintenance contract
C-1002,Beta LLC,Finance,$75000.50,03/01/2023,02/28/2025,Goods,Office supply procurement
C-1003,Gamma Inc,IT Department,$250000.00,06/01/2024,05/31/2027,Services,Network infrastructure upgrade
"""

SAMPLE_CSV_MISSING_FIELDS = """Contract Number,Vendor Name,Department,Contract Amount,Start Date,End Date,Contract Type,Description
,Alpha Services,Public Works,,01/15/2024,,Services,Some work
C-2002,,Finance,$10000.00,,,Goods,
"""

SAMPLE_CSV_BLANK_ROWS = """Contract Number,Vendor Name,Department,Contract Amount,Start Date,End Date,Contract Type,Description
C-3001,Delta Corp,Parks,$5000.00,01/01/2024,12/31/2024,Services,Park cleanup

,,,,,,,,
C-3002,Epsilon Ltd,HR,$8000.00,02/01/2024,01/31/2025,Goods,Furniture
"""


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------


class TestParseDate:
    def test_mm_dd_yyyy(self):
        assert _parse_date("01/15/2024") == date(2024, 1, 15)

    def test_yyyy_mm_dd(self):
        assert _parse_date("2024-01-15") == date(2024, 1, 15)

    def test_mm_dd_yy(self):
        assert _parse_date("01/15/24") == date(2024, 1, 15)

    def test_none_value(self):
        assert _parse_date(None) is None

    def test_empty_string(self):
        assert _parse_date("") is None

    def test_whitespace(self):
        assert _parse_date("   ") is None

    def test_unparseable(self):
        assert _parse_date("not-a-date") is None

    def test_stripped(self):
        assert _parse_date("  01/15/2024  ") == date(2024, 1, 15)


class TestParseAmount:
    def test_plain_number(self):
        assert _parse_amount("150000.00") == 150000.00

    def test_dollar_sign(self):
        assert _parse_amount("$75000.50") == 75000.50

    def test_commas(self):
        assert _parse_amount("$1,250,000.00") == 1250000.00

    def test_none_value(self):
        assert _parse_amount(None) is None

    def test_empty_string(self):
        assert _parse_amount("") is None

    def test_non_numeric(self):
        assert _parse_amount("N/A") is None


class TestParseCsvRows:
    def test_basic_parsing(self):
        rows = _parse_csv_rows(SAMPLE_CSV)
        assert len(rows) == 3
        assert rows[0]["document_number"] == "C-1001"
        assert rows[0]["vendor_name"] == "Acme Corp"
        assert rows[0]["issuing_department"] == "Public Works"
        assert rows[0]["total_amount"] == 150000.00
        assert rows[0]["effective_date"] == date(2024, 1, 15)
        assert rows[0]["expiration_date"] == date(2026, 1, 14)
        assert rows[0]["contract_type"] == "Services"
        assert rows[0]["title"] == "Road maintenance contract"

    def test_missing_fields(self):
        rows = _parse_csv_rows(SAMPLE_CSV_MISSING_FIELDS)
        assert len(rows) == 2
        # First row: no contract number, no amount, no end date
        assert rows[0]["document_number"] is None
        assert rows[0]["vendor_name"] == "Alpha Services"
        assert rows[0]["total_amount"] is None
        assert rows[0]["expiration_date"] is None
        # Second row: no vendor, no dates
        assert rows[1]["document_number"] == "C-2002"
        assert rows[1]["vendor_name"] is None
        assert rows[1]["title"] is None  # empty description

    def test_blank_rows_skipped(self):
        rows = _parse_csv_rows(SAMPLE_CSV_BLANK_ROWS)
        assert len(rows) == 2
        assert rows[0]["document_number"] == "C-3001"
        assert rows[1]["document_number"] == "C-3002"

    def test_empty_csv(self):
        rows = _parse_csv_rows("")
        assert rows == []

    def test_header_only(self):
        rows = _parse_csv_rows("Contract Number,Vendor Name\n")
        assert rows == []

    def test_raw_extraction_stored(self):
        rows = _parse_csv_rows(SAMPLE_CSV)
        assert "raw" in rows[0]
        assert rows[0]["raw"]["Contract Number"] == "C-1001"
        assert rows[0]["raw"]["Vendor Name"] == "Acme Corp"


# ---------------------------------------------------------------------------
# Integration tests — mock both HTTP download and DB session
# ---------------------------------------------------------------------------


def _make_mock_db(existing_doc_numbers: list[str] | None = None):
    """Create a mock AsyncSession that tracks added objects."""
    mock_db = AsyncMock()
    added_objects: list = []

    def track_add_all(objects):
        added_objects.extend(objects)

    def track_add(obj):
        added_objects.append(obj)

    mock_db.add_all = MagicMock(side_effect=track_add_all)
    mock_db.add = MagicMock(side_effect=track_add)
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()

    # Mock the existing-records query for dedup
    existing_rows = []
    if existing_doc_numbers:
        existing_rows = [(num, None) for num in existing_doc_numbers]

    mock_result = MagicMock()
    mock_result.all.return_value = existing_rows
    mock_db.execute = AsyncMock(return_value=mock_result)

    mock_db._added_objects = added_objects
    return mock_db


@pytest.mark.asyncio
async def test_ingest_socrata_endpoint_success(client):
    """Mocked CSV download + DB — should import 3 records."""
    mock_db = _make_mock_db()

    with (
        patch("app.api.ingest._download_csv", new_callable=AsyncMock) as mock_dl,
        patch("app.api.ingest.get_db", return_value=mock_db),
    ):
        mock_dl.return_value = SAMPLE_CSV
        # Override the dependency
        from app.api.ingest import router as ingest_router
        from app.database import get_db as real_get_db

        async def override_get_db():
            return mock_db

        from app.main import app

        app.dependency_overrides[real_get_db] = override_get_db
        try:
            response = await client.post("/api/v1/ingest/socrata")
        finally:
            app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 3
    assert data["skipped"] == 0
    assert "complete" in data["message"].lower()


@pytest.mark.asyncio
async def test_ingest_socrata_endpoint_with_duplicates(client):
    """When DB already has records, those should be skipped."""
    mock_db = _make_mock_db(existing_doc_numbers=["C-1001", "C-1002"])

    with patch("app.api.ingest._download_csv", new_callable=AsyncMock) as mock_dl:
        mock_dl.return_value = SAMPLE_CSV

        from app.database import get_db as real_get_db
        from app.main import app

        async def override_get_db():
            return mock_db

        app.dependency_overrides[real_get_db] = override_get_db
        try:
            response = await client.post("/api/v1/ingest/socrata")
        finally:
            app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 1
    assert data["skipped"] == 2


@pytest.mark.asyncio
async def test_ingest_socrata_empty_csv(client):
    """An empty CSV should return 0 imported."""
    mock_db = _make_mock_db()

    with patch("app.api.ingest._download_csv", new_callable=AsyncMock) as mock_dl:
        mock_dl.return_value = "Contract Number,Vendor Name\n"

        from app.database import get_db as real_get_db
        from app.main import app

        async def override_get_db():
            return mock_db

        app.dependency_overrides[real_get_db] = override_get_db
        try:
            response = await client.post("/api/v1/ingest/socrata")
        finally:
            app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 0
    assert data["skipped"] == 0


@pytest.mark.asyncio
async def test_ingest_socrata_download_failure(client):
    """If CSV download fails, return 502."""
    with patch("app.api.ingest._download_csv", new_callable=AsyncMock) as mock_dl:
        mock_dl.side_effect = Exception("Connection timeout")

        from app.database import get_db as real_get_db
        from app.main import app

        mock_db = _make_mock_db()

        async def override_get_db():
            return mock_db

        app.dependency_overrides[real_get_db] = override_get_db
        try:
            response = await client.post("/api/v1/ingest/socrata")
        finally:
            app.dependency_overrides.clear()

    assert response.status_code == 502


@pytest.mark.asyncio
async def test_ingest_socrata_missing_fields(client):
    """Rows with missing fields should still import successfully."""
    mock_db = _make_mock_db()

    with patch("app.api.ingest._download_csv", new_callable=AsyncMock) as mock_dl:
        mock_dl.return_value = SAMPLE_CSV_MISSING_FIELDS

        from app.database import get_db as real_get_db
        from app.main import app

        async def override_get_db():
            return mock_db

        app.dependency_overrides[real_get_db] = override_get_db
        try:
            response = await client.post("/api/v1/ingest/socrata")
        finally:
            app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 2
