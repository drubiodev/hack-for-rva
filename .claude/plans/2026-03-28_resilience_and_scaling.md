# ContractIQ — Resilience & Scaling Enhancements

> Sprint plan for hardening the pipeline against edge cases, large files, failures, and demo-day risks.

---

## Context

ContractIQ processes contract PDFs through an AI pipeline (OCR → classify → extract → validate). The current implementation works for happy-path demos but has critical gaps:
- 8000-char truncation misses expiration dates on long contracts
- No timeouts or retries on Azure calls — a slow API stalls the entire demo
- 100MB+ PDFs crash the server (full file loaded into memory)
- Scanned PDFs over 4MB fail Azure DI's upload limit
- Pipeline failures show a generic red badge with no explanation
- Server restarts leave documents stuck in intermediate states forever

These enhancements address every identified failure mode while staying within the existing architecture (FastAPI + PostgreSQL + Azure — no Celery, no Redis).

---

## Sprint Stories — MUST-HAVE

### S1: Smart Text Truncation for Long Contracts

**As a** procurement analyst uploading a 50-page contract,
**I want** the AI to find the expiration date even if it's on page 40,
**so that** I don't have to manually read every page.

**Problem:** `extractor.py` truncates to `ocr_text[:8000]` — only captures pages 1-4. Expiration dates, renewal clauses, and bond requirements are typically on pages 30-40.

**Implementation:**
- Add `_smart_truncate(text: str, budget: int = 8000) -> str` to `procurement/backend/app/extraction/extractor.py`
- Scan full OCR text for keyword windows (500-char blocks containing: "expir", "terminat", "renew", "end date", "insurance", "bond", "indemnif", "not to exceed", "commence")
- Assemble: first 2500 chars + top keyword windows (up to 4000 chars) + last 1500 chars
- Insert `[...page gap...]` markers between sections so the LLM knows there are gaps
- Replace `ocr_text[:8000]` with `_smart_truncate(ocr_text)`

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] Contract 25000012048 (8 pages, embedded text) extracts expiration date with same or better quality as before
- [ ] A 50+ page document with expiration date on page 35 extracts that date (test with Contract 23000012317 — 275 pages)
- [ ] Keyword windows include passages with "expir", "terminat", "renew"
- [ ] Total assembled text stays within 8000-char budget
- [ ] All existing backend tests pass

---

### S2: Pipeline Timeouts and Retry

**As a** user uploading a document during peak Azure load,
**I want** the system to retry failed API calls instead of silently returning empty results,
**so that** I get extracted data even when Azure is briefly slow.

**Problem:** No timeout on `AsyncOpenAI` or Azure DI calls. If Azure returns 429 or hangs for 60s, the pipeline silently returns null fields. User sees "extracted" with all N/A fields and no explanation.

**Implementation:**
- Add `timeout=httpx.Timeout(30.0)` to `AsyncOpenAI` constructor in `extractor.py` and `classifier.py`
- Wrap Azure DI poller result with `asyncio.wait_for(poller.result(), timeout=120)`
- Add simple async retry utility (3 attempts, exponential backoff: 2s, 4s, 8s) — no tenacity dependency needed
- Apply retry to all three external calls (DI OCR, classify, extract)
- On final failure, store specific error message: "Classification failed: Azure OpenAI timeout after 30s (3 attempts)"
- Update `pipeline.py` with per-step try/except and specific error messages

**Files:** `extractor.py`, `classifier.py`, `azure_di.py`, `pipeline.py`

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] AsyncOpenAI client has explicit 30s timeout in both classifier and extractor
- [ ] Azure DI has 120s timeout via `asyncio.wait_for`
- [ ] Retry logic attempts 3 times with 2s/4s/8s backoff
- [ ] After final failure, `doc.error_message` contains specific step and error type (not "Processing pipeline failed unexpectedly")
- [ ] Successful pipeline still completes normally (retry doesn't add latency on success)
- [ ] All existing backend tests pass

---

### S3: PDF Chunking for Large Scanned Documents

**As a** analyst uploading a 200-page scanned contract,
**I want** the OCR to process it in chunks instead of failing,
**so that** I don't have to manually split the PDF.

**Problem:** Azure DI rejects local file uploads over 4MB. Contract 23000004767 (6.7MB, 224 pages) fails entirely. The pipeline catches the error but the user gets no extracted data.

**Implementation:**
- Add `_split_and_ocr(file_path: str, max_chunk_bytes: int = 3_500_000) -> tuple[str, float]` to `azure_di.py`
- Use pypdf's `PdfReader`/`PdfWriter` to split into page-range chunks that fit under the limit
- OCR each chunk via Azure DI, concatenate text, average confidence
- If total pages exceed a safety limit (e.g., 100 pages), OCR first 100 pages and note truncation in a log
- Fall back gracefully: if splitting fails, return empty text with error message

**Files:** `procurement/backend/app/ocr/azure_di.py`

**Effort:** 1.5 hours

**Acceptance Criteria:**
- [ ] A 6.7MB scanned PDF (Contract 23000004767) processes successfully via chunked OCR
- [ ] Resulting text concatenates in page order
- [ ] Confidence score is the average across all chunks
- [ ] PDFs under 4MB still process normally (no splitting needed)
- [ ] A 500-page PDF only OCRs first 100 pages (budget protection)
- [ ] All existing backend tests pass

---

### S4: Error Display on Document Detail Page

**As a** user whose document failed processing,
**I want** to see what went wrong and have a way to retry,
**so that** I can take corrective action instead of being stuck.

**Problem:** The frontend never renders `doc.error_message`. User sees a red "error" badge with no context. The "Reprocess" button only appears for supervisors.

**Implementation:**
- In `procurement/frontend/src/app/dashboard/documents/[id]/page.tsx`, add an error banner after the stepper (when `doc.status === "error"` and `doc.error_message` exists)
- Red bordered card with AlertCircle icon, the error message text, and a "Reprocess" button
- Also show error_message as progress text during processing states (e.g., "Step 2/4: Classifying document...")
- Reprocess button available to both analyst and supervisor for error-state documents

**Files:** `procurement/frontend/src/app/dashboard/documents/[id]/page.tsx`

**Effort:** 30 minutes

**Acceptance Criteria:**
- [ ] Error state shows red banner with the specific error message from `doc.error_message`
- [ ] "Reprocess" button is visible on error-state documents for all roles
- [ ] Clicking Reprocess triggers the reprocess mutation and document returns to "uploading" state
- [ ] Documents without errors don't show the banner
- [ ] `npx tsc --noEmit` passes

---

### S5: Stale Document Recovery on Startup

**As a** system administrator,
**I want** documents stuck in intermediate states to be automatically marked as failed on server restart,
**so that** users aren't confused by permanently "processing" documents.

**Problem:** If the server restarts while a BackgroundTask is running, the document is stuck at "uploading", "ocr_complete", or "classified" forever. No recovery mechanism exists.

**Implementation:**
- In `procurement/backend/app/main.py` lifespan function, after `init_db()`:
- Query documents with status in ("uploading", "ocr_complete", "classified") and `updated_at` older than 10 minutes
- Set status to "error", error_message to "Processing interrupted — please click Reprocess to retry"
- Log how many documents were recovered

**Files:** `procurement/backend/app/main.py`

**Effort:** 20 minutes

**Acceptance Criteria:**
- [ ] On startup, documents stuck in processing states for >10 minutes are marked as "error"
- [ ] Error message is user-friendly and mentions Reprocess
- [ ] Recently-updated processing documents (< 10 min) are NOT touched
- [ ] Documents in final states (extracted, approved, rejected, error) are NOT touched
- [ ] Startup log shows count of recovered documents
- [ ] All existing backend tests pass

---

### S6: Date Range Validation Rule

**As a** procurement analyst reviewing AI-extracted data,
**I want** obviously wrong dates (year 1900, year 2099) to be flagged,
**so that** I catch AI hallucinations before submitting for approval.

**Problem:** The LLM sometimes hallucinates dates. No validation rule catches impossible dates — only specific expiration windows (30/90 days) and date-logic (expiration before effective) are checked.

**Implementation:**
- Add `DATE_RANGE` rule to `procurement/backend/app/validation/engine.py`
- Flag any extracted date (document_date, effective_date, expiration_date) before 2000 or after 2035 as warning severity
- Message: "Date {field} ({value}) seems unlikely — verify against original document"

**Files:** `procurement/backend/app/validation/engine.py`

**Effort:** 15 minutes

**Acceptance Criteria:**
- [ ] A document with expiration_date of "1900-01-01" triggers DATE_RANGE warning
- [ ] A document with expiration_date of "2099-12-31" triggers DATE_RANGE warning
- [ ] A document with expiration_date of "2027-06-15" does NOT trigger the rule
- [ ] Rule fires on all three date fields (document_date, effective_date, expiration_date)
- [ ] All existing backend tests pass plus new test for DATE_RANGE

---

### S7: Magic Bytes File Validation

**As a** system defending against malicious uploads,
**I want** file type to be verified by content (not just extension),
**so that** renamed executables or scripts cannot be saved to the server.

**Problem:** Upload endpoint only checks file extension. A file named `malware.pdf` with executable content passes validation, gets saved to disk, and is sent to pypdf/Azure DI.

**Implementation:**
- After writing the temp file in the upload endpoint (`router.py`), read first 8 bytes
- Verify magic bytes: PDF (`%PDF`), PNG (`\x89PNG`), JPEG (`\xFF\xD8\xFF`), TIFF (`\x49\x49\x2A\x00` or `\x4D\x4D\x00\x2A`)
- If magic bytes don't match any accepted type, delete temp file and return 400 with "File content does not match expected type"

**Files:** `procurement/backend/app/api/router.py`

**Effort:** 15 minutes

**Acceptance Criteria:**
- [ ] A real PDF passes validation
- [ ] A .txt file renamed to .pdf is rejected with 400
- [ ] Error message says "File content does not match expected type"
- [ ] Temp file is deleted on rejection
- [ ] All existing upload tests pass (update test for new validation if needed)

---

### S8: Streaming File Upload (Memory Protection)

**As a** server handling large file uploads,
**I want** to stream files to disk without loading them fully into memory,
**so that** a 100MB upload doesn't crash the server.

**Problem:** `content = await file.read()` loads the entire file into RAM. A 100MB PDF uses 100MB of server memory before the size check even runs. With concurrent uploads, this compounds.

**Implementation:**
- Replace `content = await file.read()` with a chunked read loop (64KB chunks)
- Write each chunk to the temp file immediately
- Count bytes as they stream — abort early if exceeding `max_file_size_mb`
- If aborted, delete the partial temp file and return 400
- Compute magic bytes from the first chunk (combines with S7)

**Files:** `procurement/backend/app/api/router.py`

**Effort:** 30 minutes

**Acceptance Criteria:**
- [ ] A 1MB PDF uploads successfully (functional equivalence)
- [ ] A file exceeding 20MB is rejected before fully reading into memory
- [ ] Memory usage during upload stays bounded (no spike proportional to file size)
- [ ] Upload response shape is identical to current behavior
- [ ] All existing upload tests pass

---

## Sprint Stories — NICE-TO-HAVE

### S9: Duplicate Upload Detection via File Hash

**As a** analyst who accidentally uploaded the same contract twice,
**I want** the system to detect the duplicate and point me to the existing record,
**so that** I don't create redundant work.

**Implementation:**
- Add `file_hash VARCHAR(64)` column to Document model
- Compute SHA-256 while streaming to disk (combines with S8)
- Before creating the document record, query for existing doc with same hash
- If found, return the existing document with a note "This file was previously uploaded"

**Files:** `models/document.py`, `router.py`

**Effort:** 45 minutes

**Acceptance Criteria:**
- [ ] Uploading the same PDF twice returns the first document's record (not 201)
- [ ] Different PDFs with different content create separate records
- [ ] Hash is stored in the `file_hash` column
- [ ] Response includes indication that this was a duplicate

---

### S10: Concurrent Pipeline Semaphore

**As a** server processing multiple uploads simultaneously,
**I want** a concurrency limit on the pipeline,
**so that** 10 concurrent uploads don't exhaust CPU and memory.

**Implementation:**
- Add `_pipeline_semaphore = asyncio.Semaphore(3)` at module level in `pipeline.py`
- Wrap pipeline body in `async with _pipeline_semaphore:`
- Use `asyncio.to_thread()` for pypdf `extract_text_layer` (CPU-bound work) in `service.py`

**Files:** `pipeline.py`, `service.py`

**Effort:** 20 minutes

**Acceptance Criteria:**
- [ ] No more than 3 documents process concurrently
- [ ] 4th upload queues and processes when a slot opens
- [ ] Event loop stays responsive during pypdf parsing (to_thread offloads CPU work)

---

### S11: Azure DI Page Budget Tracker

**As a** team managing a 500 pages/month free tier,
**I want** the system to track Azure DI page usage and degrade gracefully when approaching the limit,
**so that** we don't exhaust our quota mid-demo.

**Implementation:**
- Module-level counter in `azure_di.py` tracking pages sent since startup
- Configurable limit (default 400 pages) via `AZURE_DI_PAGE_BUDGET` env var
- When budget exceeded, skip Azure DI and return empty text with warning
- Log warning: "Azure DI page budget exhausted — using text-layer extraction only"

**Files:** `azure_di.py`, `config.py`

**Effort:** 30 minutes

**Acceptance Criteria:**
- [ ] Counter increments by page count after each successful DI call
- [ ] When counter exceeds budget, Azure DI is skipped with warning
- [ ] Text-layer PDFs still process normally (they don't use DI)
- [ ] Counter resets on server restart (acceptable for hackathon)

---

### S12: Upload Rate Limiter

**As a** system protecting against upload spam,
**I want** to limit uploads to 5 per user per 5 minutes,
**so that** a single user can't exhaust Azure quotas.

**Implementation:**
- In-memory dict `_upload_timestamps: dict[str, list[datetime]]` keyed by `uploaded_by`
- Before accepting upload, check last 5 minutes of timestamps for this user
- If >= 5 uploads, return 429 "Too many uploads — please wait a few minutes"
- Clean up old entries on each check

**Files:** `router.py`

**Effort:** 30 minutes

**Acceptance Criteria:**
- [ ] 5 uploads within 5 minutes succeed
- [ ] 6th upload within 5 minutes returns 429
- [ ] Different users have independent limits
- [ ] After waiting 5 minutes, user can upload again

---

### S13: Demo Cache for Offline Mode

**As a** presenter whose Azure services went down during the demo,
**I want** the system to serve pre-cached results for demo documents,
**so that** the demo continues smoothly.

**Implementation:**
- Pre-process 3-5 demo documents and save complete pipeline output (OCR text, classification, extracted fields, validation results) as JSON fixtures in `procurement/backend/fixtures/`
- Extend PLACEHOLDER handling in classifier/extractor to load fixtures by filename match
- Document the "demo mode" flow in the plan

**Files:** `classifier.py`, `extractor.py`, new `fixtures/` directory

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] With PLACEHOLDER credentials, known demo documents return realistic cached results
- [ ] Unknown documents still return empty results (no hallucinated cache)
- [ ] Fixtures are human-readable JSON

---

### S14: Optimized List Query

**As a** dashboard loading 1,365 Socrata contracts,
**I want** the document list to load fast without fetching unnecessary data,
**so that** the dashboard doesn't stall on page load.

**Problem:** Document model uses `lazy="selectin"` on validations, activity, and reminders. List endpoint loads all relationships for every document even though it only needs extracted_fields for vendor/amount/expiration.

**Implementation:**
- In list_documents endpoint, use `.options(noload(Document.validations), noload(Document.activity), noload(Document.reminders))`
- Only `selectinload(Document.extracted_fields)` is needed for the summary

**Files:** `router.py`

**Effort:** 30 minutes

**Acceptance Criteria:**
- [ ] List endpoint returns same data as before
- [ ] SQL query count reduced (verify with SQLAlchemy echo or logging)
- [ ] Page load time improves measurably with 1,365+ documents
- [ ] Detail endpoint still loads all relationships (unchanged)

---

## QA Verification Plan

After implementing any story, QA agent must verify:

1. **Backend tests pass:** `cd procurement/backend && .venv/bin/python -m pytest -v --tb=short`
2. **Frontend type-check:** `cd procurement/frontend && npx tsc --noEmit`
3. **Frontend build:** `cd procurement/frontend && npm run build`
4. **E2E smoke test (for pipeline changes):**
   - Start server: `cd procurement/backend && .venv/bin/uvicorn app.main:app --port 8000`
   - Upload a text-layer PDF: `curl -X POST localhost:8000/api/v1/documents/upload -F "file=@.../Contract 25000012048.pdf" -F "uploaded_by=QA"`
   - Wait 30s, check status is "extracted" with non-null vendor and amount
   - Upload a scanned PDF (if S3 is implemented): same test with Contract 24000006048.pdf
5. **Specific acceptance criteria** listed per story above

---

## Implementation Priority Order

```
S1 Smart truncation        ████████████ 1h    ← Highest extraction quality impact
S2 Timeouts + retry        ████████████ 1h    ← Demo reliability
S4 Error display           ██████ 30m         ← User can see what went wrong
S6 Date range validation   ███ 15m            ← Catches AI hallucinations
S7 Magic bytes             ███ 15m            ← Security, 5 lines
S5 Stale doc recovery      ████ 20m           ← Prevents zombie docs
S8 Streaming upload        ██████ 30m         ← Memory protection
S3 PDF chunking            ██████████████ 1.5h ← Unblocks 224-page contract
─────────────────────────────────────────────
Total MUST-HAVE:           ~5.5 hours

S14 Query optimization     ██████ 30m
S10 Concurrency semaphore  ████ 20m
S9  Duplicate detection    ████████ 45m
S12 Rate limiter           ██████ 30m
S11 DI budget tracker      ██████ 30m
S13 Demo cache             ████████████ 1h
─────────────────────────────────────────────
Total NICE-TO-HAVE:        ~3.5 hours
```
