# Procurement Document Processing — Agent & Team Context

> Every teammate reads this file on spawn. Keep it concise and authoritative.

## Project Overview

AI-powered procurement document processing system for HackathonRVA 2026. City staff upload scanned procurement documents (contracts, RFPs, invoices), AI extracts structured data, validates for consistency, and surfaces risks on a live dashboard — using real City of Richmond contract data. 48-hour hackathon, ~$65 budget.

**Pillar:** A Thriving City Hall (Pillar 1)
**Problem:** #2 — Helping City Staff Review Procurement Risks and Opportunities (Score: 22/32)
**Reference:** `pillar-thriving-city-hall/CHALLENGE.md`

## Architecture (non-negotiable)

```
Staff uploads PDF/image → FastAPI backend → Azure Blob Storage (store original)
                                                  ↓
                                        Azure Document Intelligence (OCR)
                                                  ↓
                                        Azure OpenAI GPT-4.1-nano (classify + extract)
                                                  ↓
                                        Validation Engine (13 rules + AI)
                                                  ↓
                                        Supabase PostgreSQL (structured data)
                                                  ↓
                           Next.js 16 Dashboard ← REST API (5s detail, 30s list polling)

Also ingests: Socrata CSV (xqn7-jvv2) with ~1,362 real City contracts
```

| Layer | Tech | Directory |
|---|---|---|
| Backend API | FastAPI, SQLAlchemy 2.0 async, OpenAI SDK, Azure DI, Azure Blob | `procurement/backend/` |
| Frontend | Next.js 16, shadcn/ui, TanStack Query, Recharts | `procurement/frontend/` |
| OCR | Azure Document Intelligence (`prebuilt-read`) | external |
| AI | Azure OpenAI GPT-4.1-nano | external |
| Storage | Azure Blob Storage + Supabase PostgreSQL | external |
| Data Sources | Socrata CSV, 10 pre-staged contract PDFs, SAM.gov (cached) | `pillar-thriving-city-hall/procurement-examples/` |
| Deployment | Railway (both services) | external |
| API Contract | OpenAPI 3.1.0 | `procurement/docs/openapi.yaml` |

## Hard Guardrails

### Product Guardrails (from challenge)
- **Never make legal compliance determinations** — surface information for staff review only
- **Never claim to represent official City procurement records** — label as "decision-support tool"
- **All AI extractions labeled "AI-assisted, requires human review"**
- **Analysts cannot approve their own reviews** — separation of duties
- **Use real City data** — Socrata CSV + pre-staged PDFs from `pillar-thriving-city-hall/procurement-examples/`
- **Socrata CSV download, NOT API** — API has known bug returning only 8 of 9 columns

### Architecture Guardrails
- **No LangChain** — use OpenAI SDK `response_format` directly for structured output
- **No Celery / No Redis** — `FastAPI BackgroundTasks` for the async OCR→extract→validate pipeline
- **GPT-4.1-nano for classification + extraction** — $0.10/1M tokens, ~$0.002 per document
- **`procurement/docs/openapi.yaml` is the single source of truth** for frontend/backend interaction
- **Processing pipeline runs as BackgroundTask** — upload returns 202 immediately
- **Azure Document Intelligence `prebuilt-read`** — not prebuilt-invoice/contract (too rigid)
- **SAM.gov: pre-cache only** — 10 req/day limit for non-federal users, never call live in demo

## Approval Workflow

```
uploaded → processing → extracted → analyst_review → pending_approval → approved | rejected → (back to analyst_review)
```

- **Analyst:** uploads, reviews extracted fields, resolves warnings, submits for approval
- **Supervisor:** approves/rejects with comments, can override fields, can reprocess
- Role selected via simple login screen (name + role, stored in localStorage, no auth)

## Key Directories

```
procurement/
  backend/app/
    ocr/           # Azure Blob Storage upload, Azure Document Intelligence OCR
    extraction/    # Document classifier + per-type field extractor (GPT-4.1-nano)
    validation/    # 13 rule-based checks + AI consistency validation
    api/           # REST endpoints: /api/v1/documents, /api/v1/analytics, /api/v1/approvals
    models/        # SQLAlchemy 2.0: Document, ExtractedFields, ValidationResult, ActivityLog
    schemas/       # Pydantic request/response schemas
    pipeline.py    # Orchestrates: OCR → classify → extract → validate
    config.py      # Pydantic BaseSettings (env vars)
    database.py    # Async engine + session factory
    main.py        # FastAPI app entry point

  frontend/src/    # Next.js 16 App Router

  docs/
    openapi.yaml   # API contract (single source of truth)

pillar-thriving-city-hall/
  procurement-examples/
    pdfs/          # 10 real Richmond contract PDFs
    txt/           # Pre-OCR'd text versions of those PDFs
```

## Data Sources

- **Socrata CSV** — `data.richmondgov.com/api/views/xqn7-jvv2/rows.csv?accessType=DOWNLOAD` (~1,362 contracts)
- **10 Real Contract PDFs** — `pillar-thriving-city-hall/procurement-examples/pdfs/`
- **Pre-OCR'd text** — `pillar-thriving-city-hall/procurement-examples/txt/`

## Skills Available

| Skill | Use for |
|---|---|
| `product-manager` | OKRs, feature prioritization, demo narrative |
| `architect` | Architecture enforcement, OpenAPI maintenance |
| `designer` | UI/UX style guide, Richmond civic color palette, accessibility, component patterns |
| `backend-dev` | FastAPI, Azure OpenAI, Azure DI, Azure Blob, SQLAlchemy patterns |
| `frontend-dev` | Next.js 16, shadcn/ui, TanStack Query, Recharts |
| `review` | Context-aware code review with guardrail checks |
| `security-audit` | File upload validation, CORS, secrets, injection vectors |
| `e2e-test` | Playwright e2e tests against deployed Railway URL |
| `deploy-check` | Railway pre-deployment checklist and smoke tests |
| `debug-pipeline` | OCR pipeline debugging (upload → OCR → classify → extract → validate → DB) |
| `commit` | Conventional commits with guardrail scanning |
| `build-with-agent-team` | Orchestrate multi-agent builds with tmux split panes |

## Frontend Warning

Next.js 16 has breaking changes from prior versions. Always read the relevant guide in `procurement/frontend/node_modules/next/dist/docs/` before writing frontend code. Do not rely on training data for Next.js APIs.

## Team

- **Priyesh** — Backend (FastAPI, AI pipeline, Azure integrations)
- **Daniel** — Frontend (Next.js dashboard)

## Agent Team Conventions

- Each teammate should own **separate files** — never have two teammates editing the same file
- Use `procurement/docs/openapi.yaml` as the coordination contract between backend and frontend teammates
- Backend teammates: run `cd procurement/backend && python -m pytest` to verify changes
- Frontend teammates: run `cd procurement/frontend && npx tsc --noEmit` to type-check
- Aim for **5-6 tasks per teammate** with clear deliverables
- Always shut down teammates before cleaning up the team

## Phase Completion Checklist

At the end of every implementation phase, the lead (or a designated teammate) MUST:

1. **OpenAPI sync check** — verify `procurement/docs/openapi.yaml` matches all implemented endpoints
2. **Backend tests pass** — run `cd procurement/backend && .venv/bin/python -m pytest -v`
3. **Frontend type-check** — run `cd procurement/frontend && npx tsc --noEmit`
4. **Disclaimer check** — "AI-assisted, requires human review" visible on all extraction views
5. **Role gating** — analyst cannot see approve button; supervisor can
6. **Git commit** — conventional commit message before starting next phase

## Implementation Plan

Full phased plan with approval workflow, DB schema, API endpoints, validation rules, QA test plan, and demo script:
→ `.claude/plans/2026-03-27_procurement_processing_plan.md`
