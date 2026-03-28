# Chat Source Documents — Feature Refinement

> **Status:** Ready for implementation
> **Date:** 2026-03-28
> **Problem:** Chat responses don't always return the actual documents backing the answer

---

## 1. Current State Audit

| Intent | Returns Sources? | Problem |
|---|---|---|
| `semantic_search` | Yes (from Azure AI Search) | Working — returns ranked docs with relevance scores |
| `aggregation` | **No** | Returns group totals only — no underlying documents |
| `expiration_alert` | Yes (from SQL) | Working — each expiring doc is a source |
| `compliance_check` | Yes (from SQL) | Working — each gap doc is a source |
| `vendor_lookup` | Yes (from SQL) | Working |
| `filter_list` | Yes (from SQL) | Working |
| `general_knowledge` | No (by design) | Correct — no documents needed |
| `comparison` | Falls through to semantic_search | Working |

**The gap:** `aggregation` queries (e.g., "total contract value for DPU") return summary numbers but **zero source documents**. The user sees "$3.5B across 399 documents" but can't click through to any of them.

**Secondary gap:** For all intents that DO return sources, the sources are clickable in the chat UI but the user has no way to see *why* each document was relevant — the snippet/caption is only shown on hover as a tooltip, and SQL-sourced documents have no snippet at all.

---

## 2. Design: Every Answer Backed by Clickable Documents

### Principle
> Every chat answer that references documents MUST return those documents as clickable sources. If the AI says "399 documents in PUBLIC_UTILITIES," the user should be able to see a representative sample.

### 2.1 Aggregation → Sources via "Top N" Backing Documents

After computing the aggregation, fetch the top documents that contributed to each group. This gives the user proof behind the numbers.

**Implementation:**

```python
# In execute_query, after aggregation:
if intent == "aggregation":
    agg_results = await sql_aggregation(...)
    # ... existing context_parts logic ...

    # NEW: Fetch top backing documents for the aggregation
    backing_docs = await sql_filter_list(
        db, sql_filters=sql_filters, limit=8
    )
    for doc in backing_docs:
        sources.append({
            "id": doc["id"],
            "title": doc["title"],
            "relevance": 0.9,
            "caption": f"{doc['vendor_name'] or 'N/A'} — "
                       f"${doc['total_amount']:,.0f}"
                       if doc['total_amount'] else None,
        })
```

**Result:** "Total DPU spend: $3.5B" now shows 8 clickable source documents — the highest-value contracts backing that number.

### 2.2 Enrich All SQL Sources with Captions

Currently, SQL-sourced documents (expiration, compliance, vendor, filter) return `caption: null`. Add a one-line summary for each:

```python
# Helper to build a caption from document fields
def _doc_caption(doc: dict) -> str:
    parts = []
    if doc.get("vendor_name"):
        parts.append(doc["vendor_name"])
    if doc.get("total_amount"):
        parts.append(f"${doc['total_amount']:,.0f}")
    if doc.get("primary_department"):
        parts.append(doc["primary_department"].replace("_", " ").title())
    if doc.get("expiration_date"):
        parts.append(f"exp {doc['expiration_date']}")
    return " — ".join(parts) if parts else None
```

### 2.3 Deduplicate Sources

When hybrid queries (e.g., vendor_lookup) run both SQL and semantic search, the same document can appear twice. Deduplicate by document ID, keeping the higher relevance score.

### 2.4 Cap Sources at 8

More than 8 source chips in the UI is overwhelming. Cap at 8, sorted by relevance descending.

---

## 3. Implementation

### Single file change: `procurement/backend/app/search/client.py`

**Changes:**

1. Add `_doc_caption()` helper
2. In `aggregation` branch: fetch backing documents via `sql_filter_list`
3. In all SQL branches: add `caption` field using `_doc_caption()`
4. Add `_deduplicate_sources()` helper at the end of `execute_query`
5. Cap sources at 8

---

## 4. Stories

### SD-1: Aggregation queries return backing documents
**As a** user asking "total spend for DPU",
**I want** to see the actual contracts behind the number,
**So that** I can drill into the data backing the aggregation.

**AC:**
- [ ] Aggregation responses include up to 8 source documents
- [ ] Sources are the highest-value contracts matching the aggregation filters
- [ ] Each source has a caption with vendor + amount

### SD-2: All sources include descriptive captions
**As a** user viewing source chips in chat,
**I want** to see a brief description on hover,
**So that** I can decide which document to open without guessing.

**AC:**
- [ ] SQL-sourced documents include caption (vendor, amount, department, expiry)
- [ ] Semantic search sources keep their existing extractive captions
- [ ] Caption shown as tooltip on hover in the UI

### SD-3: Deduplicate and cap sources
**As a** user,
**I want** clean, non-duplicated source lists,
**So that** the UI isn't cluttered with repeated documents.

**AC:**
- [ ] No duplicate document IDs in sources
- [ ] Maximum 8 sources per response
- [ ] Sorted by relevance descending
