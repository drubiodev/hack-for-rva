---
description: Context-aware code review — auto-runs git diff, detects backend/frontend/full-stack scope, applies relevant guardrails and quality checks
---

Perform a thorough code review of recent changes in the HackathonRVA Procurement Document Processing project.

---

## Step 1: Gather changes

Run `git diff HEAD` to see all uncommitted changes. If the working tree is clean, run `git diff HEAD~1` to review the most recent commit and note that you are reviewing a committed change.

Identify which layers changed:
- Files under `procurement/backend/` → apply **Backend review**
- Files under `procurement/frontend/` → apply **Frontend review**
- `procurement/docs/openapi.yaml` or both backend and frontend → apply **API contract review**
- Root config, Dockerfile, Azure Container Apps config → apply **Deployment review**

---

## Step 2: Guardrail scan — run on all changes before anything else

These are hard architecture violations. Flag each one as `BLOCK` and do not continue to style review until addressed.

| Pattern | File scope | Violation |
|---|---|---|
| `import langchain` / `from langchain` | `procurement/backend/` | Plan mandates OpenAI SDK directly — no LangChain |
| `from celery` / `import celery` | `procurement/backend/` | Plan mandates FastAPI BackgroundTasks |
| `import redis` / `Redis(` | `procurement/backend/` | Plan mandates PostgreSQL for persistence |
| `new WebSocket(` / `EventSource(` | `procurement/frontend/` | Plan mandates TanStack Query polling |
| Hardcoded API key, token, or 32+ char secret string | Anywhere | Secrets must be in environment variables |
| `output: "standalone"` removed from `next.config.ts` | `procurement/frontend/` | Azure Container Apps Docker build will be 2GB+ |
| Sync `Session` from SQLAlchemy in async endpoint | `procurement/backend/` | Deadlocks under concurrent load |
| Inline `fetch()` call inside a React component | `procurement/frontend/` | Must use `src/lib/api.ts` functions only |
| `prebuilt-invoice` or `prebuilt-contract` DI model | `procurement/backend/` | Must use `prebuilt-read` — prebuilt models are too rigid |

---

## Step 3: Backend review (apply if `procurement/backend/` files changed)

### Async correctness
- All database operations use `await` with `AsyncSession` — no blocking calls in async functions
- No `time.sleep()` or sync file I/O in request handlers
- `BackgroundTasks.add_task()` used for the OCR→extract→validate pipeline after upload

### Azure integrations
- Azure Blob Storage: upload via `azure-storage-blob` SDK, not raw HTTP
- Azure Document Intelligence: `prebuilt-read` model only (not prebuilt-invoice/contract)
- Azure OpenAI: `response_format={"type": "json_object"}` for structured extraction — no manual JSON parsing
- All prompts in `extraction/prompts.py` — no inline prompt strings

### API design
- Upload returns 202, not 200 — processing happens asynchronously
- All response shapes match `procurement/docs/openapi.yaml` field names exactly
- Pydantic response models on every endpoint — no bare `dict` returns
- Document status transitions are valid: uploading → ocr_complete → classified → extracted → validated → reviewed

### Security
- File upload validates MIME type (PDF, PNG, JPG, TIFF only) and size (max 20MB)
- Filename sanitized before storage (no path traversal)
- No SQL string formatting — SQLAlchemy ORM or parameterized queries
- AI-extracted data goes through Pydantic validation before DB write
- CORS `allow_origins` is explicit list, never `"*"`
- No secrets in source code

---

## Step 4: Frontend review (apply if `procurement/frontend/` files changed)

### Data fetching
- All fetch calls in `src/lib/api.ts` — none inline in components
- `useQuery` with `refetchInterval: 5_000` for document detail (processing status)
- `useQuery` with `refetchInterval: 30_000` for document list and analytics
- `useMutation` + `queryClient.invalidateQueries()` after review action
- TypeScript types in `src/lib/types.ts` — field names match `procurement/docs/openapi.yaml`

### File upload
- Drag-and-drop zone validates file type before upload
- Upload uses `FormData` with `multipart/form-data`
- After upload, redirect to detail page showing processing status

### Next.js App Router
- `output: "standalone"` present in `next.config.ts`
- `"use client"` used only on interactive leaf components, not on layouts
- No `window` or `document` access outside `"use client"` components

### Environment
- No hardcoded backend URL strings — always `process.env.NEXT_PUBLIC_API_URL`

---

## Step 5: API contract review

- All modified endpoints reflected in `procurement/docs/openapi.yaml`
- `src/lib/types.ts` field names match the spec exactly
- No breaking changes without explicit callout
- Document status enum values consistent across spec, backend, and frontend

---

## Output format

```
## Guardrail Scan
✅ No violations  OR  🚨 [N] blocking violations:
  - BLOCK: [pattern] in [file:line] — [rule]

## [Backend / Frontend / API Contract] Review

### Critical (must fix before demo)
- ...

### Warnings (should fix)
- ...

### Suggestions (nice to have)
- ...

## Overall
[2–3 sentence assessment.]
```

Do not invent issues to sound thorough. If a section has nothing to flag, say "No issues found."
