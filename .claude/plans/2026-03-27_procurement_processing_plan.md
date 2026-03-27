# Procurement Document Processing — Phased Implementation Plan

## Context

**Pillar:** A Thriving City Hall (Pillar 1)
**Problem:** #2 — Helping City Staff Review Procurement Risks and Opportunities (Score: 22/32)
**Hackathon:** HackathonRVA 2026 (48 hours, ~$65 budget)
**Team:** Priyesh (backend), Daniel (frontend)

City staff rely on multiple contract sources — City contracts, VITA state contracts, GSA federal contracts, cooperative purchasing agreements. Key details (expiration dates, renewal windows, pricing terms) are buried in PDFs or spread across different systems. No unified view exists. Staff manually scan PDFs and databases to make procurement decisions.

**Key sentence:** By Sunday, we will show a prototype that helps procurement staff identify expiring contracts and extract key terms from contract PDFs using real City of Richmond data, without claiming to make compliance determinations.

---

## Success Criteria (Mapped to Rubric)

| Category | Weight | Target Score | How We Hit It |
|----------|--------|-------------|---------------|
| **Impact** | **5** | 4-5 | Directly addresses Problem 2. Uses real Socrata contract data + real contract PDFs |
| **User Value** | 4 | 4-5 | Specific user (procurement analyst). Saves 20-40 min/doc. Surfaces expiring contracts automatically |
| **Feasibility** | 3 | 4 | Uses public data. Azure free tiers. Could pilot in Q3. No City system integration needed |
| **Innovation** | 3 | 3-4 | AI extraction + validation on real procurement docs. Multi-source contract view |
| **Execution** | 3 | 4-5 | Working demo with real data. Upload → extract → validate → review flow |
| **Equity** | 3 | 3 | Reduces burden on understaffed procurement team. Plain English summaries of legal docs |

**Target score:** 78-90 / 105

---

## User Personas & Roles

### Maria Torres — Procurement Analyst
- Uploads and processes documents
- Reviews AI-extracted fields, resolves validation warnings
- Submits completed reviews for supervisor approval
- **Can:** upload, review, edit fields, submit for approval
- **Cannot:** approve her own reviews, reprocess without supervisor OK

### James Chen — Procurement Supervisor
- Approves or rejects analyst reviews
- Can override extracted fields
- Sees the risk dashboard and analytics
- **Can:** approve, reject with comments, override fields, reprocess
- **Cannot:** N/A (full access)

### System Admin (stretch)
- Bulk operations, data management
- For hackathon: supervisor role covers this

---

## Document Lifecycle (with Approval Flow)

```
                    ┌─────────────────────────────────────┐
                    │         PROCESSING (automated)       │
                    │                                      │
 uploaded ──► ocr_complete ──► classified ──► extracted    │
                    │                           │          │
                    └───────────────────────────┼──────────┘
                                                ▼
                                          analyst_review
                                                │
                                     Analyst reviews fields,
                                     resolves warnings,
                                     submits for approval
                                                │
                                                ▼
                                        pending_approval
                                           /          \
                              Supervisor  /            \ Supervisor
                              approves   /              \ rejects
                                        ▼                ▼
                                   approved          rejected
                                                        │
                                              Goes back to analyst
                                              with supervisor notes
                                                        │
                                                        ▼
                                                analyst_review (again)
```

**Status enum:** `uploading | ocr_complete | classified | extracted | analyst_review | pending_approval | approved | rejected | error`

---

## Data Sources (Real, Pre-staged)

| Source | Type | Records | Status |
|--------|------|---------|--------|
| **City Contracts Socrata CSV** (xqn7-jvv2) | Structured CSV | ~1,362 contracts | Verified, use CSV download (API has 8-of-9 column bug) |
| **10 Real Contract PDFs** | Scanned PDFs + OCR text | 10 contracts | Pre-staged in `pillar-thriving-city-hall/procurement-examples/` |
| **SAM.gov** | Federal contracts API | N/A | Free key required, 10 req/day limit — pre-cache |
| **eVA** | Virginia state procurement CSV | N/A | Available on data.virginia.gov |

**Critical:** Use the CSV download for Socrata, NOT the API:
```
https://data.richmondgov.com/api/views/xqn7-jvv2/rows.csv?accessType=DOWNLOAD
```

---

## Architecture

```
                     ┌────────────────────────────────────────────────────────┐
                     │                  Railway Project                       │
                     │                                                        │
  ┌──────────┐      │  ┌─────────────────────┐     ┌──────────────────────┐  │
  │  Staff    │──────│──▶  Next.js 16         │     │  FastAPI Backend     │  │
  │  Browser  │◀─────│──│  Dashboard          │────▶│                      │  │
  └──────────┘      │  │  (shadcn/ui)        │     │  /api/v1/documents   │  │
                     │  └─────────────────────┘     │  /api/v1/analytics   │  │
  Role Selector:     │                               │  /api/v1/approvals   │  │
  [Analyst]          │                               └──┬──────┬──────┬────┘  │
  [Supervisor]       │                                  │      │      │       │
                     └──────────────────────────────────│──────│──────│───────┘
                                                        │      │      │
                              ┌──────────────────────────┘      │      └──────┐
                              ▼                                 ▼             ▼
                   ┌──────────────────┐              ┌─────────────┐  ┌──────────────┐
                   │  Azure Blob      │              │ Azure OpenAI │  │ Supabase     │
                   │  Storage         │              │ GPT-4.1-nano │  │ PostgreSQL   │
                   │  (PDF originals) │              │ (classify +  │  │ (structured  │
                   └──────────────────┘              │  extract)    │  │  data)       │
                                                     └──────┬──────┘  └──────────────┘
                   ┌──────────────────┐                     │
                   │  Azure Document  │◄────────────────────┘
                   │  Intelligence    │  (OCR for scanned PDFs;
                   │  (prebuilt-read) │   skip for text-based PDFs)
                   └──────────────────┘

  Phase 1 also ingests:
  ┌─────────────────────────────────────┐
  │  Socrata CSV (xqn7-jvv2)           │  ~1,362 City contracts
  │  Pre-staged contract PDFs (10)      │  Real Richmond contracts
  └─────────────────────────────────────┘
```

---

## Database Schema

### documents
```sql
id UUID PK,
filename VARCHAR(255), original_filename VARCHAR(255),
blob_url TEXT,  -- Azure Blob Storage URL (null for Socrata-sourced records)
source VARCHAR(30) DEFAULT 'upload',  -- upload | socrata | sam_gov | eva
file_size_bytes INTEGER, mime_type VARCHAR(100), page_count INTEGER,

-- Processing
status VARCHAR(30) DEFAULT 'uploading',
  -- uploading|ocr_complete|classified|extracted|analyst_review|pending_approval|approved|rejected|error
error_message TEXT,

-- OCR
ocr_text TEXT, ocr_confidence NUMERIC(5,4),

-- Classification
document_type VARCHAR(30),  -- rfp|rfq|contract|purchase_order|invoice|amendment|cooperative|other
classification_confidence NUMERIC(5,4),

-- Approval flow
submitted_by VARCHAR(100),  -- analyst name
submitted_at TIMESTAMPTZ,
approved_by VARCHAR(100),   -- supervisor name
approved_at TIMESTAMPTZ,
rejection_reason TEXT,

uploaded_at TIMESTAMPTZ DEFAULT NOW(),
processed_at TIMESTAMPTZ,
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW()
```

### extracted_fields
```sql
id UUID PK, document_id UUID FK,
-- Common
title VARCHAR(500), document_number VARCHAR(100),
vendor_name VARCHAR(255), issuing_department VARCHAR(255),
total_amount NUMERIC(15,2), currency VARCHAR(3) DEFAULT 'USD',
-- Dates
document_date DATE, effective_date DATE, expiration_date DATE,
-- Contract-specific
contract_type VARCHAR(50), payment_terms VARCHAR(100),
renewal_clause TEXT, insurance_required BOOLEAN, bond_required BOOLEAN,
scope_summary TEXT,
-- Raw
raw_extraction JSONB DEFAULT '{}',
extraction_confidence NUMERIC(5,4)
```

### validation_results
```sql
id UUID PK, document_id UUID FK,
rule_code VARCHAR(50), severity VARCHAR(20),  -- error|warning|info
field_name VARCHAR(100), message TEXT, suggestion TEXT,
resolved BOOLEAN DEFAULT FALSE,
resolved_by VARCHAR(100), resolved_at TIMESTAMPTZ
```

### activity_log (audit trail)
```sql
id UUID PK, document_id UUID FK,
action VARCHAR(50),  -- uploaded|ocr_complete|classified|extracted|field_edited|warning_resolved|submitted|approved|rejected|reprocessed
actor_name VARCHAR(100), actor_role VARCHAR(30),  -- analyst|supervisor|system
details JSONB DEFAULT '{}',  -- comments, field changes, etc.
created_at TIMESTAMPTZ DEFAULT NOW()
```

---

## API Endpoints

| Method | Path | Who | Description |
|--------|------|-----|-------------|
| POST | `/api/v1/documents/upload` | Analyst | Upload PDF, start pipeline → 202 |
| GET | `/api/v1/documents` | All | List with filters (status, type, source) + pagination |
| GET | `/api/v1/documents/{id}` | All | Detail + fields + validations + activity log |
| PATCH | `/api/v1/documents/{id}/fields` | Analyst | Edit extracted fields |
| POST | `/api/v1/documents/{id}/submit` | Analyst | Submit for supervisor approval |
| POST | `/api/v1/documents/{id}/approve` | Supervisor | Approve with optional comments |
| POST | `/api/v1/documents/{id}/reject` | Supervisor | Reject with required reason |
| POST | `/api/v1/documents/{id}/reprocess` | Supervisor | Re-run AI pipeline |
| GET | `/api/v1/analytics/summary` | All | KPIs (total, by type, total value) |
| GET | `/api/v1/analytics/risks` | All | Expiring contracts, upcoming deadlines |
| GET | `/api/v1/activity` | Supervisor | Recent activity across all documents |
| POST | `/api/v1/ingest/socrata` | Admin | Import Socrata CSV into documents table |
| GET | `/health` | All | Health check |

---

## Validation Rules (13 rule-based + 1 AI)

| Rule | Severity | Logic |
|------|----------|-------|
| MISSING_AMOUNT | warning | No dollar amount on contract/PO |
| DATE_LOGIC | error | Expiration before effective date |
| CONTRACT_EXPIRING_30 | error | Expires within 30 days |
| CONTRACT_EXPIRING_90 | warning | Expires within 90 days |
| CONTRACT_EXPIRED | error | Already expired |
| HIGH_VALUE_NO_BOND | warning | >$100K contract, no bond |
| AMOUNT_RANGE | warning | Amount > $10M (likely OCR error) |
| LOW_OCR_CONFIDENCE | warning | OCR confidence < 85% |
| LOW_CLASSIFICATION | warning | Classification confidence < 75% |
| MISSING_VENDOR | warning | No vendor name extracted |
| MISSING_EXPIRATION | warning | No expiration date (contract/PO) |
| MISSING_INSURANCE | info | >$50K contract, no insurance clause |
| MISSING_DATE | warning | No document date found |
| AI_CONSISTENCY | varies | GPT checks for cross-field consistency and red flags |

---

## Guardrails (Non-Negotiable)

### Product Guardrails
- **Never make legal compliance determinations** — surface information for staff review only
- **Never claim to represent official City procurement records** — label as "decision-support tool"
- **All AI extractions labeled "AI-assisted, requires human review"**
- **Analysts cannot approve their own reviews** — separation of duties
- **Use real City data** — Socrata CSV + pre-staged PDFs, not synthetic data

### Architecture Guardrails
- **No LangChain** — OpenAI SDK `response_format` directly
- **No Celery/Redis** — FastAPI BackgroundTasks
- **GPT-4.1-nano only** — ~$0.002 per document
- **`procurement/docs/openapi.yaml` is the contract** between frontend/backend
- **Upload returns 202** — pipeline runs as BackgroundTask
- **Socrata CSV download, NOT API** — API has known 8-of-9 column bug
- **SAM.gov: pre-cache, never live during demo** — 10 req/day limit

---

## Phased Implementation

### Phase 1 — Foundations (Hours 0-6)

**Goal:** Both services running, DB schema created, Socrata data ingested, first PDF processable.

| ID | Task | Owner | Effort | Acceptance Criteria |
|----|------|-------|--------|---------------------|
| BE-01 | Project scaffold | Backend | 1h | `uvicorn app.main:app` starts, `/health` returns ok |
| BE-02 | Config + DB models + schemas | Backend | 2h | All 4 tables created on startup. Pydantic schemas compile. |
| BE-03 | Socrata CSV ingester | Backend | 1.5h | `POST /api/v1/ingest/socrata` loads ~1,362 contracts into `documents` + `extracted_fields` tables with source='socrata' |
| FE-01 | Project scaffold | Frontend | 1.5h | Dev server runs, shadcn installed, TanStack Query wraps app |
| FE-02 | API layer + types + role selector | Frontend | 1.5h | Types match OpenAPI. Role selector stores name+role in localStorage. |
| INT-01 | Azure resource setup | Both | 1h | Blob container exists, DI resource provisioned, OpenAI accessible |

**Phase 1 Gate:**
- [ ] Backend serves `/health`
- [ ] Socrata data loaded (1,362+ rows visible via `GET /api/v1/documents?source=socrata`)
- [ ] Frontend dev server renders role selector
- [ ] Azure services reachable
- [ ] `git commit` with conventional message

---

### Phase 2 — AI Pipeline (Hours 6-16)

**Goal:** Upload a PDF → OCR → classify → extract → validate. Full pipeline works end-to-end.

| ID | Task | Owner | Effort | Acceptance Criteria |
|----|------|-------|--------|---------------------|
| BE-04 | Azure Blob Storage upload | Backend | 1.5h | File uploaded, blob_url stored in DB |
| BE-05 | Azure Document Intelligence OCR | Backend | 2h | Pre-staged contract PDF → text extracted with confidence score |
| BE-06 | Document classifier (GPT-4.1-nano) | Backend | 1.5h | Correctly classifies "contract" from OCR text |
| BE-07 | Field extractor (per-type prompts) | Backend | 2.5h | Extracts vendor, amount, dates, terms from contract text |
| BE-08 | Validation engine (13 rules + AI) | Backend | 2h | At least 8 rules implemented. Flags found on pre-staged contracts |
| BE-09 | Pipeline orchestrator | Backend | 1.5h | `process_document()` chains OCR→classify→extract→validate as BackgroundTask |
| BE-10 | Upload + list + detail endpoints | Backend | 2h | Upload returns 202. List/detail return correct data. |
| FE-03 | Dashboard layout + sidebar | Frontend | 1.5h | Sidebar with Upload, Documents, Dashboard links. Role badge in header. |

**Phase 2 Gate:**
- [ ] Upload one of the 10 pre-staged PDFs → pipeline completes → extracted fields visible via API
- [ ] At least 1 validation warning generated on a real contract
- [ ] Sidebar navigation works
- [ ] Backend tests pass (at least health + upload + list)
- [ ] `git commit`

---

### Phase 3 — Dashboard + Review Flow (Hours 16-28)

**Goal:** Full document list, detail view with extracted fields, approval workflow works.

| ID | Task | Owner | Effort | Acceptance Criteria |
|----|------|-------|--------|---------------------|
| BE-11 | Approval endpoints (submit/approve/reject) | Backend | 2h | Analysts can submit, supervisors can approve/reject. Role validation enforced. |
| BE-12 | Activity log + field edit endpoints | Backend | 1.5h | All actions logged. Fields editable by analyst before submit. |
| BE-13 | Analytics + risks endpoints | Backend | 1.5h | Summary KPIs. Risk list shows contracts expiring in 30/60/90 days from Socrata data. |
| FE-04 | Upload page (drag-and-drop) | Frontend | 2.5h | Drop zone accepts PDF/image. Shows progress. Redirects to detail. |
| FE-05 | Document list page | Frontend | 3h | Table with filters (status, type, source). Status badges. Pagination. |
| FE-06 | Document detail page | Frontend | 3.5h | Processing stepper, extracted fields card, OCR text panel, validation alerts, activity timeline, approval buttons (role-dependent) |
| FE-07 | Analytics/risk dashboard | Frontend | 2.5h | KPI cards (from Socrata data). Expiring contracts table. Risk alerts. |

**Phase 3 Gate:**
- [ ] Analyst can: upload → view extracted fields → edit a field → resolve a warning → submit for approval
- [ ] Supervisor can: see pending approvals → approve with comment → reject with reason
- [ ] Rejected document goes back to analyst_review status
- [ ] Activity timeline shows all actions with actor names and roles
- [ ] Risk dashboard shows real expiring contracts from Socrata CSV
- [ ] Frontend type-check passes
- [ ] `git commit`

---

### Phase 4 — Polish + Integration (Hours 28-40)

**Goal:** Production-quality demo. All 10 pre-staged contracts processed. Dark mode. Responsive. Tests.

| ID | Task | Owner | Effort | Acceptance Criteria |
|----|------|-------|--------|---------------------|
| BE-14 | Process all 10 pre-staged contracts | Backend | 1.5h | All 10 PDFs from `procurement-examples/` processed and in DB with extracted fields |
| BE-15 | Backend tests (API, pipeline, approval) | Backend | 2h | 20+ tests covering upload, list, detail, approval flow, validations |
| BE-16 | Seed script combining Socrata + PDFs | Backend | 1h | Single command loads demo-ready data |
| FE-08 | Polling + dark mode + error boundaries | Frontend | 2h | 5s polling on detail, 30s on list. Dark mode toggle. error.tsx + loading.tsx |
| FE-09 | Empty states + responsive + disclaimer banners | Frontend | 2h | Empty states with icons. Mobile table scroll. "AI-assisted" disclaimer on all extraction views |
| INT-02 | OpenAPI contract sync | Both | 1h | Spec matches implementation |
| INT-03 | Railway deployment | Both | 1h | Both services deploy. Health check passes. |
| INT-04 | End-to-end smoke test | Both | 1.5h | Upload → process → review → approve full flow works on deployed URL |

**Phase 4 Gate:**
- [ ] All 10 pre-staged contracts visible in dashboard with extracted fields
- [ ] Socrata data (~1,362 contracts) visible in risk dashboard
- [ ] Full approval flow works (upload → analyst review → submit → supervisor approve)
- [ ] "AI-assisted, requires human review" disclaimer visible on all extraction views
- [ ] Backend: 20+ tests pass
- [ ] Frontend: `tsc --noEmit` clean, `npm run build` succeeds
- [ ] Deployed to Railway and accessible
- [ ] `git commit`

---

### Phase 5 — Demo Prep (Hours 40-48)

**Goal:** Demo-ready. Rehearsed. Backup plan.

| ID | Task | Owner | Effort |
|----|------|-------|--------|
| DEMO-01 | Rehearse 3-5 min demo script | Both | 1h |
| DEMO-02 | Pre-load demo data (processed contracts + Socrata) | Backend | 0.5h |
| DEMO-03 | Screenshot backup for each demo step | Frontend | 0.5h |
| DEMO-04 | Final bug fixes | Both | 2h |

---

## QA Test Plan

### Backend Tests (pytest)

| Suite | Tests | What's Verified |
|-------|-------|-----------------|
| test_health.py | 1 | Health endpoint returns ok |
| test_upload.py | 4 | Upload accepts PDF/PNG/JPG/TIFF, rejects EXE, rejects >20MB, returns 202 |
| test_documents.py | 8 | List (empty, with data, filtered by status/type/source), detail (found, 404), pagination |
| test_approval.py | 6 | Submit (analyst only), approve (supervisor only), reject (supervisor, reason required), reject→resubmit cycle, analyst cannot approve own |
| test_validation.py | 5 | DATE_LOGIC, CONTRACT_EXPIRING, MISSING_AMOUNT, LOW_OCR_CONFIDENCE, AMOUNT_RANGE |
| test_socrata.py | 3 | Socrata ingest loads data, date normalization, handles missing fields |
| test_activity.py | 3 | Upload logged, approval logged, rejection logged with reason |

**Total: 30 tests minimum**

### Frontend Checks

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| TypeScript | `npx tsc --noEmit` | Zero errors |
| Build | `npm run build` | Compiles, all routes generated |
| Role-gating | Manual | Analyst view: no approve button. Supervisor view: approve + reject buttons visible |
| Disclaimer | Manual | "AI-assisted" banner visible on every extraction view |

### E2E Smoke Test (manual or Playwright)

1. **As Analyst:** Upload `Contract 24000006048.pdf` → watch stepper → verify extracted fields (vendor: Insight Public Sector, amount present) → edit one field → resolve one warning → submit for approval
2. **As Supervisor:** See pending approval → review fields → approve with comment "Verified"
3. **Risk dashboard:** Verify Socrata data shows expiring contracts → click one → see detail
4. **Rejection flow:** As analyst, submit new doc → as supervisor, reject → verify analyst sees rejection reason → resubmit → approve

---

## Demo Script (3-5 minutes)

### 1. The Pain (30s)
"A Richmond procurement officer needs to review 50 contracts this month. Each one is a scanned PDF — 20 to 80 pages. She manually reads each one, types key terms into a spreadsheet. 30 minutes per contract. And if she misses a renewal date, the City could lose hundreds of thousands of dollars."

### 2. The Dashboard (45s)
- Show the risk dashboard loaded with **real Socrata data** — 1,362 City contracts
- "We ingested Richmond's actual open contract data. Right now, 8 contracts expire in the next 60 days."
- Point to the risk panel: expiring contracts, vendor concentration

### 3. Live Upload (60s)
- Drag a **real** Richmond contract PDF onto the upload zone
- Watch the processing stepper: OCR → Classify → Extract → Validate
- "In 20 seconds, the AI read 40 pages and extracted every critical field."
- Show extracted fields: vendor name, contract value, expiration date, renewal clause
- Show validation warnings: "Contract expires in 67 days" / "No bond requirement on $287K contract"
- Point to the "AI-assisted" disclaimer

### 4. Approval Flow (45s)
- As Analyst: review fields, resolve a warning, click "Submit for Approval"
- Switch role to Supervisor: see the pending approval, review, click "Approve"
- Show the activity timeline: every action logged with name, role, timestamp
- "Separation of duties — the analyst who processes can't approve their own work."

### 5. Close (30s)
"We built this in 48 hours using real City of Richmond contract data and Azure free tiers. This is a decision-support tool — it surfaces the information, staff make the call. Next step: a RAG chatbot so staff can ask 'What did we spend on IT consulting last quarter?' and get an answer from their document archive."

---

## What We Are Explicitly NOT Building

- Legal compliance determinations
- Automated contract award decisions
- Integration with internal City systems (Oracle RAPIDS, AvePoint)
- Authentication (role selector is a demo convenience)
- RAG chatbot (Phase 2)
- Batch upload (Phase 2)

---

## Verification Plan

1. `cd procurement/backend && .venv/bin/python -m pytest -v` — 20+ tests pass
2. `cd procurement/frontend && npx tsc --noEmit` — zero errors
3. `cd procurement/frontend && npm run build` — compiles successfully
4. OpenAPI sync: all endpoints match `procurement/docs/openapi.yaml`
5. E2E: upload pre-staged PDF → pipeline completes → fields extracted → review works
6. Socrata data: ~1,362 contracts visible in risk dashboard with real vendor names and dates
7. Disclaimer: "AI-assisted, requires human review" visible on every extraction view
8. Role selector: analyst and supervisor see appropriate actions
9. CSV export: extracted data downloadable as CSV
10. All 10 pre-staged contracts processed with plausible extracted fields

---

---

# ADDENDUM — Pre-Implementation Critical Review (2026-03-27)

> Written after reviewing constraints, rubric, City tech inventory, and challenge guidance a final time. These changes override conflicting sections above.

---

## A1. Strategic Reframing: View Layer, Not New System

### The Problem With Our Original Plan
The original plan builds a standalone FastAPI + Next.js application with its own database, its own document storage, and its own approval workflow. This is **another system for the City to maintain** — the opposite of what the rubric rewards under Feasibility ("Could this be piloted within a year?").

### The Fix: Frame as a View Layer on the City's Own Data
Our tool does NOT create a parallel contract database. It:
1. **Reads from Socrata** — the City's own public contracts dataset (~1,362 records)
2. **Enhances with AI extraction** — turns uploaded PDFs into structured data in 20 seconds
3. **Exports results** — CSV/Excel download compatible with existing City workflows (Oracle RAPIDS, Excel)

**Pitch framing:** *"This is a lens on your existing data, not a replacement for your systems. The risk dashboard reads from the City's open data portal. The PDF extractor saves 30 minutes per document and exports to CSV you can paste into your existing spreadsheet."*

**Post-hackathon integration path (mention in pitch, don't build):**
- Power BI report reading live Socrata API → replaces our dashboard
- Power Automate flow triggering extraction → fits the City's Dynamics 365 / Microsoft stack
- SharePoint document library → replaces Azure Blob for PDF storage
- Richmond already runs on Microsoft (RVA311 = AvePoint on Dynamics 365, BizTalk middleware). Our tool's value is the **AI extraction logic**, which can be wrapped as an Azure Function and plugged into their existing Microsoft infrastructure.

---

## A2. Review/Approval Workflow — Phased Implementation

### Decision: Keep the full approval workflow, but phase it

The approval gating (analyst → supervisor) is important to demonstrate — it shows we understand government procurement workflows where separation of duties matters. However, it's not the core demo hero (that's the risk dashboard + AI extraction).

### Phase Strategy

**Phases 1-3 (core demo):** Simple "Reviewed by [Name], [Role]" with notes. Single status for review. This gets us to a working demo fast.

**Phase 4 (polish, if time allows):** Layer on the full approval chain — analyst submits → supervisor approves/rejects → rejection returns to analyst. The schema already supports this (the original plan's status enum and approval fields), so it's an additive change, not a rewrite.

### What This Means for Implementation

**Phases 1-3 use a simplified status:**
```
uploading | processing | extracted | reviewed | error
```

**Phase 4 expands to the full lifecycle (if time):**
```
uploading | processing | extracted | analyst_review | pending_approval | approved | rejected | error
```

The database schema from the original plan (with `submitted_by`, `approved_by`, `rejection_reason` fields) should still be created in Phase 1 — the columns just stay null until Phase 4 wires up the endpoints.

### API Phasing

**Phases 1-3 (must have):**
- `POST /api/v1/documents/{id}/review` — any role marks as reviewed with name + notes
- `GET /api/v1/documents/{id}/export/csv` — CSV download of extracted fields

**Phase 4 (should have):**
- `POST /api/v1/documents/{id}/submit` — analyst submits for approval
- `POST /api/v1/documents/{id}/approve` — supervisor approves
- `POST /api/v1/documents/{id}/reject` — supervisor rejects with reason

### Demo Narrative

If approval flow is ready: show the full analyst → supervisor → approve cycle with role switching.

If not ready: show the review action and say *"In the full version, this review feeds into a gated approval workflow — analysts submit, supervisors approve or reject with comments. The schema supports it; we prioritized extraction quality for this demo."*

---

## A3. OCR Is Core — Azure Document Intelligence Is a Must-Have

### Why OCR Cannot Be Optional
The pre-staged `.txt` files are **hackathon sample data only**. In reality, the City's procurement documents are paper-based, scanned as images. The entire value proposition is: *"Scan a paper contract → AI reads it → structured data in 20 seconds."* Without OCR, there is no product.

### OCR Strategy: Two Layers, Both Required

| Scenario | Method | Phase |
|----------|--------|-------|
| **Text-layer PDFs** | `pypdf` / `pdfplumber` text extraction | Phase 2 — fast, free, no external dependency |
| **Scanned/image PDFs** | Azure Document Intelligence `prebuilt-read` | Phase 2 — the core OCR capability |
| **Pre-staged `.txt` files** | Direct read for fast testing during development | Phase 1 only — development convenience |

### Pipeline: Try Text Layer First, Fall Back to Azure DI

```python
async def extract_text(file_path: str, blob_url: str, mime_type: str) -> tuple[str, float]:
    """Text layer first (free, instant). Azure DI for scanned docs."""
    if mime_type == "application/pdf":
        text = extract_text_layer(file_path)  # pypdf
        if text and len(text.strip()) > 100:
            return text, 1.0  # Text was embedded — perfect confidence

    # Scanned PDF or image — this is the primary use case
    return await azure_di_ocr(blob_url)
```

### What This Means for Implementation

- **Phase 1:** Azure DI resource provisioned in INT-01. Pre-staged `.txt` files used for fast iteration on classifier/extractor prompts.
- **Phase 2 (BE-05 + BE-06):** Both `pypdf` text extraction AND Azure DI OCR implemented. Pipeline auto-selects based on whether the PDF has an embedded text layer.
- **Demo:** Upload a real scanned contract PDF → Azure DI OCRs it → extraction runs → *"This contract was scanned from paper. The AI read the scan, extracted the vendor, the amount, the expiration date, and flagged that it expires in 67 days."*

### Key Extraction Targets (the insights that matter)

The OCR + extraction pipeline must surface these for every document:

| Insight | Why It Matters | Field |
|---------|---------------|-------|
| **When does the contract end?** | Missed renewals cost hundreds of thousands | `expiration_date` |
| **Which location/department is impacted?** | Staff need to know who to alert | `issuing_department`, `location` |
| **What case type is this document?** | Determines review workflow and applicable rules | `document_type`, `contract_type` |
| **Who is the vendor?** | Vendor concentration risk, debarment checks | `vendor_name` |
| **What's the dollar value?** | Threshold determines bond/insurance requirements | `total_amount` |
| **Is there a renewal clause?** | Determines whether the City has options before re-procurement | `renewal_clause` |
| **What compliance terms exist?** | Insurance, bonding, MBE/DBE requirements | `insurance_required`, `bond_required`, `required_certifications` |

These are the fields the extraction prompts must prioritize. If the OCR is noisy, focus extraction on these 7 insights over trying to capture every field perfectly.

---

## A4. Socrata Data Is the Hero — Restructured Demo Flow

### Original Demo Order
1. Hook → 2. Live upload → 3. Extracted data → 4. Validations → 5. Risk dashboard → 6. Second upload → 7. Close

### Revised Demo Order (Socrata first, extraction second)

**1. The Pain (30s)**
*"A Richmond procurement officer needs to know which contracts expire in the next 60 days. Today, they download a CSV, open it in Excel, manually sort by date, and review each one. For the detail, they open a 40-page PDF and read it cover to cover."*

**2. The Risk Dashboard — REAL DATA (60s)** ← HERO MOMENT
- Dashboard loads with **~1,362 real City of Richmond contracts** from Socrata
- *"This is the City's actual contract data — every vendor, every dollar amount, every expiration date."*
- Apply "expiring in 60 days" filter → show 5-8 real contracts in the danger zone
- Point to vendor names, department names, dollar amounts — **all real**
- KPI cards: total contracts, total value, contracts expiring this quarter

**3. Live PDF Upload — INNOVATION (60s)**
- Drag one of the 10 real contract PDFs onto the upload zone
- Processing stepper animates: Extract → Classify → Validate
- *"In 15 seconds, the AI read 40 pages and extracted every critical field."*
- Show extracted fields side-by-side with the original text
- Show validation warnings: "Contract expires in 67 days"
- Show the confidence score and "AI-assisted" disclaimer

**4. The Review + Export (30s)**
- Click "Mark as Reviewed" — enter name and notes
- Click "Export to CSV" — *"This drops into your existing Excel workflow"*

**5. Close (30s)**
*"We built this in 48 hours on the City's own open data. This isn't a new system — it's a lens that surfaces what's already there, enhanced with AI extraction. The procurement team doesn't need to learn anything new. They get a dashboard that shows risk, and a tool that reads their PDFs for them."*

*"Post-hackathon, this extraction logic can run as an Azure Function plugged into the City's existing Microsoft stack — Dynamics 365, Power Automate, SharePoint. No new infrastructure required."*

---

## A5. Equity Framing (Rubric Score: 3x Weight)

The equity category is naturally weaker for Problem 2 (staff-facing) than Problem 1 (resident-facing). Here's how we score:

- *"Every dollar saved on procurement overhead is a dollar that serves Richmond residents directly"*
- *"Understaffed procurement teams — often the first to face budget cuts — can now handle their workload without additional hires"*
- *"By surfacing contract risks early, we prevent the procurement failures that erode public trust and disproportionately impact under-resourced departments"*
- *"Plain-language AI summaries make complex legal procurement documents accessible to staff at all experience levels — not just senior procurement officers"*

---

## A6. Revised Task Breakdown (Incorporating All Changes)

### Hours Saved By Phasing Approval Workflow

| Change | Hours Saved |
|--------|-------------|
| Full approval workflow deferred to Phase 4 (not cut) | 4h deferred |
| Complex activity timeline → simplified in Phase 3, full in Phase 4 | 1.5h deferred |
| **Total deferred** | **~5.5h moved to Phase 4** |

### Reinvested Into Core Demo Quality

| Added | Hours |
|-------|-------|
| Polish extraction quality on all 10 real contracts | 2h |
| Make risk dashboard genuinely useful with Socrata data | 1.5h |
| CSV export feature (shows integration readiness) | 1h |
| Demo rehearsal and edge case handling | 1h |

### Revised Phase 2 — AI Pipeline (Hours 6-16)

OCR remains a core deliverable. Both text extraction and Azure DI:

| ID | Task | Owner | Effort | Notes |
|----|------|-------|--------|-------|
| BE-05a | Text extraction (pypdf/pdfplumber) | Backend | 1h | Text-layer PDFs — fast, free |
| BE-05b | Pre-OCR'd text loader | Backend | 0.5h | Development convenience for prompt iteration |
| BE-06 | Azure Document Intelligence OCR | Backend | 2h | Core capability — scanned/image PDFs |

### Revised Phase 3 — Dashboard + Review (Hours 16-28)

Simple review in Phase 3. Approval gating in Phase 4:

| ID | Task | Owner | Effort | Notes |
|----|------|-------|--------|-------|
| BE-11 | Review endpoint + CSV export | Backend | 1.5h | "Reviewed by [Name]" with notes + CSV download |
| BE-12 | Activity log (simplified) | Backend | 1h | Log uploads, processing, reviews, exports |

### Revised Phase 4 — Polish + Approval Workflow (Hours 28-40)

| ID | Task | Owner | Effort | Notes |
|----|------|-------|--------|-------|
| BE-14 | Process all 10 pre-staged contracts | Backend | 1.5h | Via OCR pipeline, not pre-OCR'd text |
| BE-15 | Approval workflow endpoints | Backend | 2.5h | submit/approve/reject, role enforcement, status expansion to 8 states |
| BE-16 | Full activity timeline | Backend | 1.5h | All actions with actor, role, comments |
| FE-10 | CSV export button on detail + list pages | Frontend | 1h | Shows integration readiness |
| FE-11 | Approval UI (if BE-15 complete) | Frontend | 2h | Submit button (analyst), approve/reject (supervisor), rejection reason modal |

---

## A7. Revised Verification Plan

1. `cd procurement/backend && .venv/bin/python -m pytest -v` — 20+ tests pass
2. `cd procurement/frontend && npx tsc --noEmit` — zero errors
3. `cd procurement/frontend && npm run build` — compiles successfully
4. OpenAPI sync: all endpoints match `procurement/docs/openapi.yaml`
5. **Socrata hero check:** Risk dashboard shows ~1,362 real contracts with real vendor names, real amounts, real dates
6. **Extraction quality:** All 10 pre-staged contracts processed with plausible vendor, amount, date, type fields
7. **Validation flags:** At least 3 different validation rules fire across the 10 contracts
8. Disclaimer: "AI-assisted, requires human review" visible on every extraction view
9. **CSV export:** Download works and contains all extracted fields
10. Role selector: analyst and supervisor see their name + role in header
11. **No "new system" language in demo:** Pitch frames as "view layer on City's own open data"
12. **Real data only in demo:** No synthetic contracts shown. Every row is from Socrata or pre-staged PDFs.

---

## A8. Risk Register (Updated)

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | GPT-4.1-nano extracts wrong fields from messy OCR text | Medium | High | Test against all 10 pre-staged contracts early (Phase 2). Tune prompts. Show confidence scores. |
| 2 | Socrata data has date format inconsistencies | Medium | Medium | Normalize dates in ingestion script. Test with real CSV in Phase 1. |
| 3 | Pre-OCR'd text files have OCR artifacts | Known | Medium | Prompts include "OCR artifacts may be present — extract what is clearly legible" |
| 4 | Live PDF upload fails during demo | Medium | High | **Pre-process all 10 contracts before demo.** Upload one live as the "wow" moment, but have all data pre-loaded. |
| 5 | Judges ask "how does this integrate with the City's systems?" | High | Medium | Prepared answer: "The extraction logic runs as a standalone service today. Post-hackathon, it wraps as an Azure Function in the City's existing Microsoft stack — Dynamics 365, Power Automate, SharePoint." |
| 6 | Judges ask "is this another system to maintain?" | High | Medium | Prepared answer: "No — the dashboard reads from the City's own Socrata data. The only new capability is the AI extraction, which can be deployed as a serverless function with zero infrastructure maintenance." |
| 7 | Azure OpenAI rate limit or outage during demo | Low | Critical | Pre-process all contracts. Cache extraction results. Demo works entirely from cached data if needed. |
| 8 | Socrata API/CSV is down during demo | Low | High | Download CSV during setup. Load from local file, not live API. |
| 9 | Budget overrun on Azure | Low | Low | GPT-4.1-nano: ~$0.002/doc. 50 docs = $0.10. Blob storage: pennies. Total < $1. |
| 10 | Approval workflow takes longer than expected | Medium | Medium | Deferred to Phase 4. Simple review works in Phase 3. If Phase 4 runs short, demo simple review + pitch the approval chain as "production-ready schema, wiring in progress." |
| 11 | Azure DI free tier exhausted (500 pages/month) | Low | Medium | 10 contracts × ~5 pages avg = ~50 pages. Well within limit. Track usage. |
| 12 | Scope creep into RAG chatbot | High | High | RAG is Phase 2, period. Do not start until post-hackathon. |
