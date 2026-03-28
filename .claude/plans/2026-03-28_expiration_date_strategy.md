# ContractIQ — Expiration Date Strategy

> Root cause analysis and fix plan for the #1 pain point: contract expiration visibility.

---

## Problem Statement

**99% of documents (1,370 of 1,371) are missing expiration dates.** This is the single most critical field for the hackathon challenge — City staff need to know when contracts expire so they can plan renewals, re-procurements, or terminations. Without this, the dashboard provides no proactive risk management value.

---

## Root Cause Analysis

### Socrata Records (1,365 records — 0% have expiration dates)

The CSV **does** contain expiration dates. Every record has `Effective To` with dates like `10/13/2026 12:00:00 AM`. Two bugs prevent extraction:

| Bug | Root Cause | Impact |
|---|---|---|
| **Column name mismatch** | CSV header `Effective To` normalizes to `effective_to`, but `_get_field()` candidates list only checks `end_date`, `expiration_date`, `expire_date`, `enddate`, `contract_end_date`, `termination_date` — no `effective_to` | 1,365 records get NULL expiration |
| **Date format mismatch** | Socrata format is `MM/DD/YYYY HH:MM:SS AM` but `_parse_date()` only tries `%m/%d/%Y` (no time component) | Even if column matched, parsing would fail |

Same two bugs affect `Effective From` → `effective_from` (effective dates also missing).

**Fix: 2 lines of code + backfill.**

### Uploaded PDFs (6 records — 1 has expiration date)

- 4 of 6 uploaded PDFs are in `error` state (OCR/classification failed) — no extraction ran
- 1 extracted successfully with an expiration date (Contract 24000006048)
- 1 extracted but the expiration date was in the document body beyond the truncation window

The smart truncation (S1 from resilience plan) already addresses the long-document issue. The error-state documents need reprocessing once Azure credentials are live.

---

## Implementation

### Fix 1: Add missing column name candidates

```python
# ingest.py — _get_field candidates
effective_date_str = _get_field(
    row, col_map,
    "start_date", "effective_date", "begin_date", "startdate",
    "contract_start_date",
    "effective_from",  # ← Socrata CSV header
)
expiration_date_str = _get_field(
    row, col_map,
    "end_date", "expiration_date", "expire_date", "enddate",
    "contract_end_date", "termination_date",
    "effective_to",  # ← Socrata CSV header
)
```

### Fix 2: Handle datetime format in date parsing

```python
def _parse_date(value: str | None) -> date | None:
    if not value or not value.strip():
        return None
    value = value.strip()
    # Strip time component if present (e.g., "01/31/2011 12:00:00 AM")
    if " " in value:
        value = value.split(" ")[0]
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%y", "%Y/%m/%d"):
        ...
```

### Fix 3: Backfill existing Socrata records from raw_extraction

```python
# Read raw_extraction["Effective To"], parse it, set expiration_date
# Read raw_extraction["Effective From"], parse it, set effective_date
```

---

## Expected Outcome

| Metric | Before | After |
|---|---|---|
| Socrata with expiration_date | 0 / 1,365 | ~1,365 / 1,365 |
| Socrata with effective_date | 0 / 1,365 | ~1,365 / 1,365 |
| Upload with expiration_date | 1 / 6 | 1 / 6 (others need reprocessing) |
| **Total coverage** | **0.07%** | **~99.6%** |

This unlocks all expiration-based features: 30/60/90-day warnings, department expiration dashboard, renewal reminders.
