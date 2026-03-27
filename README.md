# RVA 311 SMS Civic Service

SMS-based 311 reporting system with AI classification, a live operations dashboard, and map view. Built for HackathonRVA 2026.

Citizens text a report to a Twilio toll-free number. GPT-4.1-nano classifies the issue (pothole, streetlight, graffiti, etc.) and extracts location. City staff see incoming requests on a real-time dashboard with map pins and analytics.

## Architecture

```
Citizen SMS --> Twilio --> FastAPI (AI classify + confirm) --> Supabase PostgreSQL
                                                                  |
                                          Next.js Dashboard <-- REST API (30s polling)
```

| Layer | Tech | Directory |
|---|---|---|
| Backend API | FastAPI, SQLAlchemy 2.0, Azure OpenAI, Twilio | [`backend/`](backend/) |
| Frontend Dashboard | Next.js 16, shadcn/ui, TanStack Query, React-Leaflet | [`frontend/`](frontend/) |
| Database | Supabase PostgreSQL (free tier) | -- |
| Deployment | Railway (both services) | -- |
| API Contract | OpenAPI 3.1.0 | [`docs/openapi.yaml`](docs/openapi.yaml) |

## Quick start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Supabase project (free tier)
- Azure OpenAI resource with `gpt-41-nano` and `gpt-4o-mini` deployments
- Twilio account with a toll-free number

### Backend

```bash
cd backend
cp .env.example .env    # fill in your credentials
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Runs on `http://localhost:8000`. Health check: `GET /health`.

See [backend/README.md](backend/README.md) for details.

### Frontend

```bash
cd frontend
cp .env.example .env.local    # set NEXT_PUBLIC_API_URL
npm install
npm run dev
```

Runs on `http://localhost:3000`. Redirects to `/dashboard`.

See [frontend/README.md](frontend/README.md) for details.

## Documentation

| Document | Description |
|---|---|
| [Product Requirements](docs/product-requirements.md) | OKRs, user stories, MoSCoW features, demo script |
| [Technical Implementation Plan](docs/technical-implementation-plan.md) | Task breakdown, ADRs, DB schema, dependency graph |
| [OpenAPI Spec](docs/openapi.yaml) | Single source of truth for FE/BE contract |

## Environment variables

### Backend (`backend/.env`)

| Variable | Description |
|---|---|
| `DATABASE_URL` | Supabase PostgreSQL connection (`postgresql+asyncpg://...`) |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_API_VERSION` | API version (default: `2025-01-01-preview`) |
| `AZURE_DEPLOYMENT_CLASSIFIER` | GPT-4.1-nano deployment name |
| `AZURE_DEPLOYMENT_RESPONDER` | GPT-4o-mini deployment name |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | Twilio toll-free number (E.164) |
| `FRONTEND_URL` | Frontend URL for CORS |
| `ENVIRONMENT` | `development` or `production` |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL |

## Team

- **Priyesh** — Backend (FastAPI, AI, SMS pipeline)
- **Daniel** — Frontend (Next.js dashboard)
