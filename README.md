# Procurement Document Processing

AI-powered procurement document processing for the City of Richmond. Staff upload scanned contracts, RFPs, and invoices — AI extracts structured data in seconds, validates for risks, and surfaces expiring contracts on a live dashboard. Built with real City data for HackathonRVA 2026.

**Pillar:** A Thriving City Hall | **Problem:** Helping City Staff Review Procurement Risks and Opportunities

> This is a decision-support tool. AI-assisted extractions require human review.

## Architecture

```mermaid
graph TB
    subgraph Client["Browser"]
        FE["Next.js 16 Dashboard<br/><i>shadcn/ui + TanStack Query</i>"]
        RS["Role Selector<br/><i>Analyst / Supervisor</i>"]
    end

    subgraph Railway["Railway"]
        API["FastAPI Backend<br/><i>SQLAlchemy 2.0 async</i>"]
    end

    subgraph Azure["Azure Services"]
        BLOB["Blob Storage<br/><i>PDF originals</i>"]
        DI["Document Intelligence<br/><i>prebuilt-read OCR</i>"]
        OAI["OpenAI GPT-4.1-nano<br/><i>classify + extract</i>"]
    end

    subgraph Data["Data Sources"]
        SOC["Socrata CSV<br/><i>~1,362 City contracts</i>"]
        PDF["10 Pre-staged PDFs<br/><i>Real Richmond contracts</i>"]
    end

    DB[("Supabase PostgreSQL")]

    RS --> FE
    FE -- "REST API<br/>(5s/30s polling)" --> API
    API -- "store original" --> BLOB
    API -- "OCR scanned docs" --> DI
    API -- "classify + extract" --> OAI
    API -- "structured data" --> DB
    SOC -- "CSV ingest" --> API
    PDF -- "upload" --> API
    DI -- "extracted text" --> API
    OAI -- "structured fields" --> API
    FE -- "reads" --> DB

    style Client fill:#e8f4fd,stroke:#2196F3
    style Railway fill:#f3e5f5,stroke:#9C27B0
    style Azure fill:#fff3e0,stroke:#FF9800
    style Data fill:#e8f5e9,stroke:#4CAF50
    style DB fill:#fce4ec,stroke:#E91E63
```

## Data Flow — Document Processing Pipeline

```mermaid
sequenceDiagram
    actor Analyst
    actor Supervisor
    participant FE as Next.js Dashboard
    participant API as FastAPI Backend
    participant Blob as Azure Blob Storage
    participant DI as Azure Doc Intelligence
    participant AI as Azure OpenAI<br/>GPT-4.1-nano
    participant VE as Validation Engine<br/>13 rules + AI
    participant DB as Supabase PostgreSQL

    Note over Analyst, DB: Upload & Processing (automated)

    Analyst->>FE: Upload contract PDF
    FE->>API: POST /documents/upload
    API-->>FE: 202 Accepted (processing started)

    API->>Blob: Store original PDF
    Blob-->>API: blob_url

    API->>DI: Send PDF for OCR
    DI-->>API: Extracted text + confidence score

    API->>AI: Classify document type
    AI-->>API: contract / rfp / invoice / ...

    API->>AI: Extract structured fields<br/>(vendor, amount, dates, terms)
    AI-->>API: JSON structured output

    API->>VE: Validate extracted fields
    Note right of VE: DATE_LOGIC, EXPIRING_30,<br/>HIGH_VALUE_NO_BOND,<br/>MISSING_AMOUNT, etc.
    VE-->>API: Validation results (errors/warnings)

    API->>DB: Save document + fields + validations
    API->>DB: Log activity (system)

    Note over Analyst, DB: Review & Approval (human)

    FE->>API: GET /documents/{id} (5s polling)
    API-->>FE: Document detail + extracted fields

    Analyst->>FE: Review fields, resolve warnings
    FE->>API: PATCH /documents/{id}/fields
    API->>DB: Update fields + log edit

    Analyst->>FE: Submit for approval
    FE->>API: POST /documents/{id}/submit
    API->>DB: Status → pending_approval

    Supervisor->>FE: Review pending document
    FE->>API: GET /documents/{id}
    API-->>FE: Document with pending_approval status

    alt Approved
        Supervisor->>FE: Approve with comments
        FE->>API: POST /documents/{id}/approve
        API->>DB: Status → approved + log
    else Rejected
        Supervisor->>FE: Reject with reason
        FE->>API: POST /documents/{id}/reject
        API->>DB: Status → rejected + log
        Note over Analyst: Document returns to analyst_review
    end
```

## Socrata Data Ingest Flow

```mermaid
sequenceDiagram
    participant Admin
    participant API as FastAPI Backend
    participant SOC as Socrata Open Data<br/>data.richmondgov.com
    participant DB as Supabase PostgreSQL

    Admin->>API: POST /ingest/socrata
    API->>SOC: Download CSV (xqn7-jvv2)
    SOC-->>API: ~1,362 rows

    loop Each CSV row
        API->>API: Normalize dates & currency
        API->>API: Map columns to schema
        API->>API: Check for duplicates
        API->>DB: Insert document (source=socrata, status=extracted)
        API->>DB: Insert extracted_fields
    end

    API->>DB: Log ingest activity
    API-->>Admin: {"imported": 1362, "skipped": 0}
```

| Layer | Tech | Directory |
|---|---|---|
| Backend API | FastAPI, SQLAlchemy 2.0 async, OpenAI SDK, Azure DI, Azure Blob | [`procurement/backend/`](procurement/backend/) |
| Frontend | Next.js 16, shadcn/ui, TanStack Query, Recharts | [`procurement/frontend/`](procurement/frontend/) |
| OCR | Azure Document Intelligence (`prebuilt-read`) | external |
| AI | Azure OpenAI GPT-4.1-nano (~$0.002/doc) | external |
| Storage | Azure Blob Storage + Supabase PostgreSQL | external |
| Data Sources | Socrata CSV, 10 pre-staged contract PDFs | [`pillar-thriving-city-hall/procurement-examples/`](pillar-thriving-city-hall/procurement-examples/) |
| API Contract | OpenAPI 3.1.0 | [`procurement/docs/openapi.yaml`](procurement/docs/openapi.yaml) |

## Key Features

- **PDF Upload + AI Extraction** — Upload scanned procurement documents, get structured fields in ~20 seconds
- **Real City Data** — ~1,362 contracts from Richmond's Socrata open data portal
- **Risk Dashboard** — Surfaces expiring contracts (30/60/90 days), missing bonds, high-value anomalies
- **13 Validation Rules + AI Consistency Check** — Catches date logic errors, missing fields, OCR issues
- **Approval Workflow** — Analyst reviews and submits, supervisor approves/rejects (separation of duties)
- **Role-Based Views** — Analyst and supervisor see appropriate actions

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Supabase project (free tier)
- Azure OpenAI, Document Intelligence, and Blob Storage resources

### Backend

```bash
cd procurement/backend
cp .env.example .env          # fill in your credentials
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

Runs on `http://localhost:8000`. Health check: `GET /health`.

### Frontend

```bash
cd procurement/frontend
npm install
npm run dev
```

Runs on `http://localhost:3000`. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`.

### Load Socrata Data

Once the backend is running:

```bash
curl -X POST http://localhost:8000/api/v1/ingest/socrata
```

Imports ~1,362 real City of Richmond contracts.

## Environment Variables

### Backend (`procurement/backend/.env`)

| Variable | Description |
|---|---|
| `DATABASE_URL` | Supabase PostgreSQL connection (`postgresql+asyncpg://...`) |
| `AZURE_BLOB_CONNECTION_STRING` | Azure Blob Storage connection string |
| `AZURE_BLOB_CONTAINER_NAME` | Blob container name (default: `procurement-docs`) |
| `AZURE_DI_ENDPOINT` | Azure Document Intelligence endpoint |
| `AZURE_DI_KEY` | Azure Document Intelligence key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name (default: `gpt-4.1-nano`) |
| `CORS_ORIGINS` | Allowed origins (default: `http://localhost:3000`) |

### Frontend (`procurement/frontend/.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL (default: `http://localhost:8000`) |

## Approval Workflow

```mermaid
stateDiagram-v2
    [*] --> uploading: Staff uploads PDF

    uploading --> ocr_complete: Azure Doc Intelligence
    ocr_complete --> classified: GPT-4.1-nano classifies
    classified --> extracted: GPT-4.1-nano extracts fields
    extracted --> analyst_review: Validation complete

    analyst_review --> pending_approval: Analyst submits

    pending_approval --> approved: Supervisor approves
    pending_approval --> rejected: Supervisor rejects

    rejected --> analyst_review: Analyst revises

    approved --> [*]

    uploading --> error: Pipeline failure
    ocr_complete --> error: Pipeline failure
    classified --> error: Pipeline failure
```

- **Analyst:** uploads, reviews extracted fields, resolves warnings, submits for approval
- **Supervisor:** approves or rejects with comments, can override fields
- Analysts cannot approve their own reviews (separation of duties)

## Tests

```bash
# Backend
cd procurement/backend
.venv/bin/python -m pytest -v        # 27 tests

# Frontend
cd procurement/frontend
npx tsc --noEmit                     # type-check
npm run build                        # build verification
```

## Team

- **Priyesh** — Backend (FastAPI, AI pipeline, Azure integrations)
- **Daniel** — Frontend (Next.js dashboard)

## License

Built for HackathonRVA 2026. Not for production use.
