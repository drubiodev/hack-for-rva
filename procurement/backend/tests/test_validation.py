"""Tests for the validation engine rules.

The engine is at app/validation/engine.py.
The engine uses `_document_type` internal field to determine contract-specific rules.
"""

from datetime import date, timedelta

import pytest

from app.validation.engine import validate_document


@pytest.mark.asyncio
async def test_date_logic_rule_fires():
    """DATE_LOGIC: expiration date before effective date should trigger an error."""
    fields = {
        "effective_date": "2025-06-01",
        "expiration_date": "2025-01-01",  # before effective
        "total_amount": 50000,
        "vendor_name": "Test Corp",
        "document_date": "2025-01-01",
        "_document_type": "contract",
    }
    results = await validate_document(fields, ocr_confidence=0.95, classification_confidence=0.90)
    rule_codes = [r["rule_code"] for r in results]
    assert "DATE_LOGIC" in rule_codes
    date_logic = next(r for r in results if r["rule_code"] == "DATE_LOGIC")
    assert date_logic["severity"] == "error"


@pytest.mark.asyncio
async def test_contract_expiring_30_rule_fires():
    """CONTRACT_EXPIRING_30: contract expiring within 30 days should trigger error."""
    soon = date.today() + timedelta(days=15)
    fields = {
        "effective_date": "2024-01-01",
        "expiration_date": soon.isoformat(),
        "total_amount": 50000,
        "vendor_name": "Test Corp",
        "document_date": "2024-01-01",
        "_document_type": "contract",
    }
    results = await validate_document(fields, ocr_confidence=0.95, classification_confidence=0.90)
    rule_codes = [r["rule_code"] for r in results]
    assert "CONTRACT_EXPIRING_30" in rule_codes


@pytest.mark.asyncio
async def test_missing_amount_rule_fires():
    """MISSING_AMOUNT: contract without total_amount should trigger a warning."""
    fields = {
        "effective_date": "2024-01-01",
        "expiration_date": "2026-12-31",
        "total_amount": None,
        "vendor_name": "Test Corp",
        "document_date": "2024-01-01",
        "_document_type": "contract",  # required for MISSING_AMOUNT check
    }
    results = await validate_document(fields, ocr_confidence=0.95, classification_confidence=0.90)
    rule_codes = [r["rule_code"] for r in results]
    assert "MISSING_AMOUNT" in rule_codes


@pytest.mark.asyncio
async def test_low_ocr_confidence_rule_fires():
    """LOW_OCR_CONFIDENCE: OCR confidence < 0.85 should trigger a warning."""
    fields = {
        "effective_date": "2024-01-01",
        "expiration_date": "2026-12-31",
        "total_amount": 50000,
        "vendor_name": "Test Corp",
        "document_date": "2024-01-01",
        "_document_type": "contract",
    }
    results = await validate_document(fields, ocr_confidence=0.70, classification_confidence=0.90)
    rule_codes = [r["rule_code"] for r in results]
    assert "LOW_OCR_CONFIDENCE" in rule_codes


@pytest.mark.asyncio
async def test_amount_range_rule_fires():
    """AMOUNT_RANGE: amount > $10M should trigger a warning for review."""
    fields = {
        "effective_date": "2024-01-01",
        "expiration_date": "2026-12-31",
        "total_amount": 15_000_000,  # $15M
        "vendor_name": "Test Corp",
        "document_date": "2024-01-01",
        "_document_type": "contract",
    }
    results = await validate_document(fields, ocr_confidence=0.95, classification_confidence=0.90)
    rule_codes = [r["rule_code"] for r in results]
    assert "AMOUNT_RANGE" in rule_codes
