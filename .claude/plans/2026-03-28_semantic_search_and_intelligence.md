# Semantic Search & Intelligence Engine — Product + Architecture Proposal

> **Status:** Draft — awaiting review
> **Date:** 2026-03-28
> **Authors:** Product Manager + Architect (Claude collaboration)
> **Budget constraint:** ~$65 total, hackathon 48h timeline
> **Depends on:** Existing extraction pipeline, Azure OpenAI, Azure SQL

---

## 1. Problem Statement

The system already extracts 30+ structured fields from procurement documents and stores full OCR text — but none of it is semantically searchable. The current chat endpoint does naive ILIKE keyword matching on `ocr_text`, which:

- Misses semantically related queries ("water infrastructure" won't match "stormwater management")
- Ignores the rich extracted metadata (amounts, departments, compliance flags, dates)
- Can't answer aggregation questions ("total value of water services contracts")
- Can't run cross-document intelligence ("which vendors have contracts expiring this quarter?")
- Has no conversation memory — every question is independent

**Goal:** Turn the existing data into a queryable intelligence layer that powers both a conversational chatbot and hardcoded application features (dashboard widgets, validation, alerts).

---

## 2. Solution Overview

### Architecture: Hybrid SQL + Semantic Search with AI Orchestration

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query / App Feature                   │
│  (chatbot question, dashboard widget, validation trigger)    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Query     │
                    │  Router     │  ← AI classifies intent
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
     ┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
     │  Structured  │ │ Semantic │ │   Hybrid    │
     │  SQL Query   │ │  Search  │ │  (both)     │
     │  (aggregates,│ │ (Azure   │ │             │
     │   filters)   │ │ AI Search│ │             │
     └──────┬──────┘ └────┬─────┘ └──────┬──────┘
            │              │              │
            └──────────────┼──────────────┘
                           │
                    ┌──────▼──────┐
                    │  Context    │
                    │  Assembler  │  ← Merges results, deduplicates
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  AI Answer  │
                    │  Generator  │  ← ChatGPT 5.4 mini with grounded context
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Response   │
                    │  + Sources  │  ← Answer, cited documents, confidence
                    └─────────────┘
```

### Why this approach?

| Alternative | Why not |
|---|---|
| Pure vector search (Pinecone, pgvector) | Additional service cost, overkill for ~1,400 docs, no SQL aggregation |
| Pure SQL full-text search | No semantic understanding, bad UX for natural language |
| Azure AI Search alone | Great for retrieval but can't do SQL aggregations |
| **Hybrid SQL + Azure AI Search** | ✅ Best of both — semantic retrieval for text, SQL for numbers/dates/aggregation |

---

## 3. Detailed Design

### 3.1 Azure AI Search Index

**Index name:** `procurement-docs`

**Index schema:**

| Field | Type | Searchable | Filterable | Sortable | Facetable | Source |
|---|---|---|---|---|---|---|
| `id` | Edm.String (key) | — | ✅ | — | — | Document.id |
| `title` | Edm.String | ✅ | — | — | — | ExtractedFields.title |
| `vendor_name` | Edm.String | ✅ | ✅ | ✅ | ✅ | ExtractedFields |
| `document_type` | Edm.String | — | ✅ | — | ✅ | Document.document_type |
| `status` | Edm.String | — | ✅ | — | ✅ | Document.status |
| `primary_department` | Edm.String | ✅ | ✅ | — | ✅ | ExtractedFields |
| `department_tags` | Collection(Edm.String) | ✅ | ✅ | — | ✅ | ExtractedFields |
| `total_amount` | Edm.Double | — | ✅ | ✅ | — | ExtractedFields |
| `scope_summary` | Edm.String | ✅ | — | — | — | ExtractedFields |
| `ocr_text` | Edm.String | ✅ | — | — | — | Document.ocr_text (truncated to 32KB) |
| `effective_date` | Edm.DateTimeOffset | — | ✅ | ✅ | — | ExtractedFields |
| `expiration_date` | Edm.DateTimeOffset | — | ✅ | ✅ | — | ExtractedFields |
| `procurement_method` | Edm.String | — | ✅ | — | ✅ | ExtractedFields |
| `mbe_wbe_required` | Edm.Boolean | — | ✅ | — | ✅ | ExtractedFields |
| `federal_funding` | Edm.Boolean | — | ✅ | — | ✅ | ExtractedFields |
| `compliance_flags` | Collection(Edm.String) | ✅ | ✅ | — | ✅ | ExtractedFields |
| `source` | Edm.String | — | ✅ | — | ✅ | Document.source |
| `upload_date` | Edm.DateTimeOffset | — | ✅ | ✅ | — | Document.uploaded_at |

**Semantic configuration:**
- Semantic ranker enabled on: `title`, `scope_summary`, `ocr_text`, `vendor_name`
- This gives us semantic re-ranking on top of BM25 keyword matching — no embeddings needed, Azure handles it

**Why no custom embeddings?**
Azure AI Search's built-in semantic ranker uses Microsoft's transformer models for re-ranking. For ~1,400 documents on a $65 budget, this is dramatically simpler and cheaper than managing an embedding pipeline. If the corpus grows past 10K docs, revisit with vector search.

### 3.2 Query Router — The Intelligence Layer

The key innovation: an AI-powered query router that classifies user intent and dispatches to the right execution path.

**Intent taxonomy:**

| Intent | Example | Execution Path |
|---|---|---|
| `semantic_search` | "contracts related to water infrastructure" | Azure AI Search (semantic) |
| `aggregation` | "total value of DPU contracts" | SQL aggregation on ExtractedFields |
| `filter_list` | "show me all sole-source contracts over $100K" | SQL WHERE + pagination |
| `compliance_check` | "which contracts are missing MBE/WBE certification?" | SQL WHERE on compliance fields |
| `expiration_alert` | "contracts expiring in next 90 days" | SQL date range query |
| `vendor_lookup` | "all contracts with Vendor X" | SQL exact + AI Search fuzzy |
| `comparison` | "compare the two stormwater contracts" | AI Search retrieve + LLM compare |
| `general_knowledge` | "what is an RFP?" | LLM direct (no retrieval needed) |
| `multi_step` | "which department spends the most on sole-source?" | SQL aggregation + GROUP BY |

**Router implementation** (ChatGPT 5.4 mini, ~50 tokens output):

```python
ROUTER_SYSTEM_PROMPT = """You are a query classifier for a procurement document system.
Given a user question, output JSON with:
{
  "intent": one of ["semantic_search", "aggregation", "filter_list",
                     "compliance_check", "expiration_alert", "vendor_lookup",
                     "comparison", "general_knowledge", "multi_step"],
  "sql_filters": {  // optional, only if intent involves SQL
    "department": str or null,
    "vendor": str or null,
    "document_type": str or null,
    "min_amount": float or null,
    "max_amount": float or null,
    "date_from": str or null,  // ISO format
    "date_to": str or null,
    "procurement_method": str or null,
    "compliance_field": str or null
  },
  "search_query": str or null,  // natural language for semantic search
  "aggregation": str or null    // "sum", "count", "avg", "max", "min"
  "aggregation_field": str or null  // field to aggregate
  "group_by": str or null       // field to group by
}"""
```

**Cost:** ~200 tokens per classification × $0.15/1M input tokens = negligible

### 3.3 SQL Intelligence Queries

For structured/aggregation intents, generate and execute parameterized SQL against Azure SQL Server. **Never raw string interpolation** — always parameterized.

**Pre-built query templates** (hardcoded for dashboard widgets + validation):

```python
INTELLIGENCE_QUERIES = {
    "total_by_department": """
        SELECT ef.primary_department,
               COUNT(*) as doc_count,
               SUM(ef.total_amount) as total_value
        FROM extracted_fields ef
        JOIN documents d ON d.id = ef.document_id
        WHERE d.status NOT IN ('failed', 'processing')
        GROUP BY ef.primary_department
        ORDER BY total_value DESC
    """,

    "expiring_soon": """
        SELECT d.id, ef.title, ef.vendor_name, ef.expiration_date, ef.total_amount
        FROM extracted_fields ef
        JOIN documents d ON d.id = ef.document_id
        WHERE ef.expiration_date BETWEEN :now AND :threshold
        AND d.status NOT IN ('failed', 'processing')
        ORDER BY ef.expiration_date ASC
    """,

    "compliance_gaps": """
        SELECT d.id, ef.title, ef.vendor_name, ef.compliance_flags,
               ef.mbe_wbe_required, ef.federal_funding
        FROM extracted_fields ef
        JOIN documents d ON d.id = ef.document_id
        WHERE (ef.mbe_wbe_required = true AND ef.mbe_wbe_status IS NULL)
           OR (ef.federal_funding = true AND ef.compliance_flags IS NULL)
    """,

    "sole_source_over_threshold": """
        SELECT d.id, ef.title, ef.vendor_name, ef.total_amount, ef.procurement_method
        FROM extracted_fields ef
        JOIN documents d ON d.id = ef.document_id
        WHERE ef.procurement_method = 'SOLE_SOURCE'
        AND ef.total_amount > :threshold
        ORDER BY ef.total_amount DESC
    """,

    "vendor_concentration": """
        SELECT ef.vendor_name,
               COUNT(*) as contract_count,
               SUM(ef.total_amount) as total_value,
               MIN(ef.expiration_date) as earliest_expiry
        FROM extracted_fields ef
        JOIN documents d ON d.id = ef.document_id
        WHERE d.status NOT IN ('failed', 'processing')
        GROUP BY ef.vendor_name
        HAVING COUNT(*) > 1
        ORDER BY total_value DESC
    """
}
```

### 3.4 Semantic Search Flow

For natural language queries that need document retrieval:

```
1. Query Router classifies intent as semantic_search or hybrid
2. Build Azure AI Search request:
   - search text = router's search_query
   - queryType = "semantic"
   - semanticConfiguration = "procurement-semantic"
   - filters from router's sql_filters (OData format)
   - top = 5-10
   - select = id, title, vendor_name, scope_summary, total_amount, department
3. Azure AI Search returns ranked results with:
   - BM25 base score
   - Semantic re-ranking score
   - Captions (extractive snippets)
4. Context Assembler formats results for LLM
5. LLM generates grounded answer with source citations
```

### 3.5 Index Population Pipeline

**When to index:**
- After pipeline.py completes extraction + validation (add hook at end of `process_document`)
- On Socrata CSV ingest completion
- Manual reindex endpoint for admin

**Implementation:**

```python
# procurement/backend/app/search/indexer.py

async def index_document(document_id: str, db: AsyncSession):
    """Push a single document's data to Azure AI Search."""
    doc = await get_document_with_fields(document_id, db)
    if not doc or not doc.extracted_fields:
        return

    search_doc = {
        "id": str(doc.id),
        "title": doc.extracted_fields.title or doc.filename,
        "vendor_name": doc.extracted_fields.vendor_name,
        "document_type": doc.document_type,
        "status": doc.status,
        "primary_department": doc.extracted_fields.primary_department,
        "department_tags": doc.extracted_fields.department_tags or [],
        "total_amount": float(doc.extracted_fields.total_amount) if doc.extracted_fields.total_amount else None,
        "scope_summary": doc.extracted_fields.scope_summary,
        "ocr_text": (doc.ocr_text or "")[:32000],  # Azure limit
        "effective_date": isoformat(doc.extracted_fields.effective_date),
        "expiration_date": isoformat(doc.extracted_fields.expiration_date),
        "procurement_method": doc.extracted_fields.procurement_method,
        "mbe_wbe_required": doc.extracted_fields.mbe_wbe_required,
        "federal_funding": doc.extracted_fields.federal_funding,
        "compliance_flags": doc.extracted_fields.compliance_flags or [],
        "source": doc.source,
        "upload_date": isoformat(doc.uploaded_at),
    }

    client = SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index,
        credential=AzureKeyCredential(settings.azure_search_key),
    )
    await client.upload_documents(documents=[search_doc])


async def reindex_all(db: AsyncSession):
    """Full reindex — called on startup or manual trigger."""
    docs = await db.execute(
        select(Document).where(Document.status.notin_(["failed", "processing"]))
    )
    batch = []
    for doc in docs.scalars():
        # ... build search_doc same as above
        batch.append(search_doc)
        if len(batch) >= 100:
            await client.upload_documents(documents=batch)
            batch = []
    if batch:
        await client.upload_documents(documents=batch)
```

### 3.6 Conversation Memory

Store conversation turns in a lightweight table for multi-turn context:

```sql
CREATE TABLE chat_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role VARCHAR(20) NOT NULL,  -- 'analyst' or 'supervisor'
    user_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES chat_conversations(id),
    role VARCHAR(10) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    sources JSONB,  -- [{document_id, title, relevance}]
    intent VARCHAR(50),  -- classified intent for analytics
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Context window management:** Include last 5 turns (user + assistant) in the LLM prompt. Summarize older turns if conversation exceeds 10 exchanges.

### 3.7 Hardcoded Intelligence Features

These are **not chatbot features** — they're application-integrated intelligence that runs automatically or on-demand from dashboard widgets.

#### 3.7.1 Intelligence Endpoints (new)

```
GET  /api/v1/intelligence/department-spend
     → Aggregated spend by department (for dashboard chart)

GET  /api/v1/intelligence/expiring?days=90
     → Documents expiring within N days (for alert widget)

GET  /api/v1/intelligence/compliance-gaps
     → Documents with missing compliance fields (for risk panel)

GET  /api/v1/intelligence/vendor-concentration
     → Vendors with multiple contracts + total exposure (for risk panel)

GET  /api/v1/intelligence/sole-source-review?threshold=50000
     → Sole-source contracts above threshold (for review queue)

GET  /api/v1/intelligence/document-type-validation/{doc_type}
     → Validation rules status for a document type (contract vs RFP vs invoice)

POST /api/v1/intelligence/custom-query
     → Natural language → SQL (authenticated, supervisor only)
     → Uses the query router to translate and execute safely
```

#### 3.7.2 Validation Rules by Document Type

Different document types have different required fields and validation rules:

```python
VALIDATION_RULES_BY_TYPE = {
    "contract": {
        "required_fields": [
            "vendor_name", "total_amount", "effective_date",
            "expiration_date", "scope_summary", "procurement_method"
        ],
        "rules": [
            ("expiration_after_effective", "Expiration date must be after effective date"),
            ("amount_positive", "Contract amount must be positive"),
            ("vendor_not_debarred", "Vendor must not appear on debarment list"),
            ("insurance_if_over_100k", "Contracts over $100K require insurance verification"),
            ("bond_if_construction", "Construction contracts require performance bond"),
            ("mbe_wbe_if_over_threshold", "Contracts over city threshold require MBE/WBE plan"),
        ]
    },
    "rfp": {
        "required_fields": [
            "title", "scope_summary", "procurement_method"
        ],
        "rules": [
            ("has_evaluation_criteria", "RFP must include evaluation criteria"),
            ("has_submission_deadline", "RFP must have submission deadline"),
        ]
    },
    "invoice": {
        "required_fields": [
            "vendor_name", "total_amount", "document_number"
        ],
        "rules": [
            ("has_matching_contract", "Invoice should reference a known contract"),
            ("amount_within_contract", "Invoice amount should not exceed contract value"),
        ]
    }
}
```

#### 3.7.3 Dashboard Intelligence Widgets

| Widget | Data Source | Refresh |
|---|---|---|
| **Department Spend Treemap** | `/intelligence/department-spend` | 30s polling |
| **Expiring Contracts Alert** | `/intelligence/expiring?days=90` | 30s polling |
| **Compliance Gap Indicators** | `/intelligence/compliance-gaps` | 30s polling |
| **Vendor Concentration Risk** | `/intelligence/vendor-concentration` | 30s polling |
| **Sole-Source Review Queue** | `/intelligence/sole-source-review` | 30s polling |

---

## 4. Implementation Plan

### Phase 1: Azure AI Search Setup + Index Population (2-3 hours)

**Files to create/modify:**

| File | Action |
|---|---|
| `procurement/backend/app/search/__init__.py` | Create — package init |
| `procurement/backend/app/search/index_schema.py` | Create — index definition + creation |
| `procurement/backend/app/search/indexer.py` | Create — document indexing (single + batch) |
| `procurement/backend/app/search/client.py` | Create — search client wrapper |
| `procurement/backend/app/pipeline.py` | Modify — add index_document call after validation |
| `procurement/backend/app/config.py` | Verify — Azure Search config already present |
| `procurement/backend/requirements.txt` | Add — `azure-search-documents>=11.6.0` |

**Deliverables:**
- [ ] Azure AI Search index created with schema above
- [ ] Semantic configuration enabled
- [ ] Single-document indexing integrated into pipeline
- [ ] Batch reindex endpoint (`POST /api/v1/admin/reindex`)
- [ ] All existing documents indexed

### Phase 2: Query Router + Enhanced Chat (2-3 hours)

**Files to create/modify:**

| File | Action |
|---|---|
| `procurement/backend/app/search/router.py` | Create — intent classification + dispatch |
| `procurement/backend/app/search/queries.py` | Create — SQL intelligence query templates |
| `procurement/backend/app/search/assembler.py` | Create — context assembly for LLM |
| `procurement/backend/app/api/router.py` | Modify — replace chat endpoint internals |
| `procurement/backend/app/models/document.py` | Modify — add ChatConversation + ChatMessage models |
| `procurement/backend/alembic/versions/xxx_chat_tables.py` | Create — migration |

**Deliverables:**
- [ ] Query router classifies intent with >90% accuracy on test queries
- [ ] Semantic search returns relevant results for natural language queries
- [ ] Aggregation queries return correct numbers
- [ ] Conversation context maintained across turns
- [ ] Sources include real relevance scores from Azure AI Search

### Phase 3: Intelligence Endpoints + Dashboard Widgets (2-3 hours)

**Files to create/modify:**

| File | Action |
|---|---|
| `procurement/backend/app/api/intelligence.py` | Create — intelligence endpoints |
| `procurement/backend/app/api/router.py` | Modify — mount intelligence router |
| `procurement/frontend/src/lib/api.ts` | Modify — add intelligence API calls |
| `procurement/frontend/src/lib/types.ts` | Modify — add intelligence types |
| `procurement/frontend/src/components/IntelligenceWidgets.tsx` | Create — widget components |
| `procurement/frontend/src/app/dashboard/page.tsx` | Modify — integrate widgets |
| `procurement/docs/openapi.yaml` | Modify — add intelligence endpoints |

**Deliverables:**
- [ ] All 5 intelligence endpoints working
- [ ] Dashboard shows department spend visualization
- [ ] Expiring contracts alert visible
- [ ] Compliance gaps surfaced
- [ ] Vendor concentration risk displayed

### Phase 4: Document-Type Validation + Polish (1-2 hours)

**Files to create/modify:**

| File | Action |
|---|---|
| `procurement/backend/app/search/validation_rules.py` | Create — type-specific validation rules |
| `procurement/backend/app/validation/engine.py` | Modify — integrate type-specific rules |
| `procurement/frontend/src/components/ChatPanel.tsx` | Modify — show intent badges, improve UX |

**Deliverables:**
- [ ] Validation rules vary by document type
- [ ] Chat shows query intent classification
- [ ] Source relevance scores displayed in chat
- [ ] End-to-end demo script validated

---

## 5. API Contract Changes (OpenAPI additions)

```yaml
# New endpoints to add to openapi.yaml

/api/v1/intelligence/department-spend:
  get:
    summary: Aggregated spend by department
    tags: [Intelligence]
    responses:
      200:
        content:
          application/json:
            schema:
              type: object
              properties:
                departments:
                  type: array
                  items:
                    type: object
                    properties:
                      department: { type: string }
                      document_count: { type: integer }
                      total_value: { type: number }

/api/v1/intelligence/expiring:
  get:
    summary: Documents expiring within N days
    tags: [Intelligence]
    parameters:
      - name: days
        in: query
        schema: { type: integer, default: 90 }
    responses:
      200:
        content:
          application/json:
            schema:
              type: object
              properties:
                documents:
                  type: array
                  items:
                    $ref: '#/components/schemas/DocumentSummary'

/api/v1/intelligence/compliance-gaps:
  get:
    summary: Documents with compliance field gaps
    tags: [Intelligence]
    responses:
      200:
        content:
          application/json:
            schema:
              type: object
              properties:
                gaps:
                  type: array
                  items:
                    type: object
                    properties:
                      document_id: { type: string, format: uuid }
                      title: { type: string }
                      vendor_name: { type: string }
                      missing_fields: { type: array, items: { type: string } }

/api/v1/intelligence/vendor-concentration:
  get:
    summary: Vendor risk concentration analysis
    tags: [Intelligence]
    responses:
      200:
        content:
          application/json:
            schema:
              type: object
              properties:
                vendors:
                  type: array
                  items:
                    type: object
                    properties:
                      vendor_name: { type: string }
                      contract_count: { type: integer }
                      total_value: { type: number }
                      earliest_expiry: { type: string, format: date }

/api/v1/intelligence/sole-source-review:
  get:
    summary: Sole-source contracts above threshold
    tags: [Intelligence]
    parameters:
      - name: threshold
        in: query
        schema: { type: number, default: 50000 }
    responses:
      200:
        content:
          application/json:
            schema:
              type: object
              properties:
                documents:
                  type: array
                  items:
                    $ref: '#/components/schemas/DocumentSummary'

# Enhanced chat request
ChatRequest:
  type: object
  required: [question]
  properties:
    question:
      type: string
      maxLength: 1000
    conversation_id:
      type: string
      format: uuid
    filters:  # NEW — allow chat to be scoped
      type: object
      properties:
        department: { type: string }
        document_type: { type: string }
        date_from: { type: string, format: date }
        date_to: { type: string, format: date }

# Enhanced chat response
ChatResponse:
  type: object
  properties:
    answer:
      type: string
    sources:
      type: array
      items:
        type: object
        properties:
          document_id: { type: string, format: uuid }
          title: { type: string }
          relevance: { type: number }  # NOW real score, not hardcoded
          snippet: { type: string }    # NEW — extractive caption
    conversation_id:
      type: string
      format: uuid
    intent:           # NEW — transparency
      type: string
    query_metadata:   # NEW — debug/transparency
      type: object
      properties:
        execution_path: { type: string }
        result_count: { type: integer }
        search_time_ms: { type: integer }
```

---

## 6. Cost Analysis

| Component | Unit Cost | Usage Estimate | Monthly Cost |
|---|---|---|---|
| Azure AI Search (Free tier) | $0 | 50MB, 3 indexes, 10K docs | **$0** |
| Azure AI Search (Basic tier, if needed) | $70/mo | 2GB, 15 indexes | **$70** — over budget |
| Azure OpenAI (query routing) | $0.15/1M input | ~500 queries × 200 tokens | **< $0.01** |
| Azure OpenAI (answer generation) | $0.60/1M output | ~500 queries × 300 tokens | **< $0.01** |
| Azure SQL (already provisioned) | $0 incremental | Chat tables ~1MB | **$0** |

**Recommendation:** Start with Azure AI Search **Free tier** (50MB, 10K documents). Our ~1,400 documents with OCR text truncated to 32KB each = ~45MB — fits within free tier. If we hit the limit, the Basic tier at $70/mo exceeds our budget so we'd fall back to SQL full-text search with the same query router architecture.

**Fallback if Azure AI Search is unavailable:** The query router + SQL intelligence queries work without Azure AI Search. Only the semantic_search intent degrades to keyword ILIKE. Everything else (aggregation, filtering, compliance checks, vendor analysis) is pure SQL.

---

## 7. Demo Script Integration

For the hackathon demo, this enables a powerful narrative:

1. **"Show me all water services contracts"** → Semantic search finds contracts mentioning water, stormwater, DPU, utilities
2. **"What's the total value?"** → Aggregation query, multi-turn context knows we're still talking about water
3. **"Any compliance gaps?"** → Intelligence endpoint surfaces missing MBE/WBE certifications
4. **"Which ones expire this quarter?"** → Date filter on the same context
5. **Dashboard auto-surfaces** — expiring contracts alert, department spend chart, vendor risk

This transforms the app from "upload and view documents" to "intelligent procurement intelligence platform."

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Azure AI Search Free tier runs out of space | Semantic search unavailable | Truncate OCR text more aggressively, or fall back to SQL full-text |
| Query router misclassifies intent | Wrong execution path, bad answer | Include "I'm not sure" as valid classification, default to hybrid |
| Aggregation returns wrong numbers | Loss of trust | Unit tests with known data, always show "AI-assisted" disclaimer |
| Azure AI Search indexing is slow | Stale search results | Index async in pipeline, show "indexing..." status |
| Conversation memory table grows | Slow queries | Auto-purge conversations older than 7 days |

---

## 9. Success Criteria

- [ ] Natural language query returns semantically relevant documents (not just keyword match)
- [ ] "Total value of contracts for [department]" returns correct aggregation
- [ ] Multi-turn conversation maintains context (follow-up questions work)
- [ ] Dashboard intelligence widgets display real-time insights
- [ ] All answers include source citations with real relevance scores
- [ ] Document-type-specific validation rules fire correctly
- [ ] Demo script runs end-to-end in under 3 minutes
- [ ] Free tier budget maintained

---

## 10. Dependencies

| Dependency | Status | Blocker? |
|---|---|---|
| Azure AI Search resource | Need to provision | Yes for semantic search, No for SQL intelligence |
| `azure-search-documents` Python SDK | Need to install | Yes for search integration |
| Existing extraction pipeline | ✅ Working | No |
| Azure OpenAI | ✅ Working | No |
| Azure SQL | ✅ Working | No |
| Frontend chat components | ✅ Working | No |
