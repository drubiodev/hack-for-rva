# RVA 311 — Backend

FastAPI backend handling SMS ingestion, AI classification, and the REST API for the dashboard.

## Structure

```
app/
├── main.py            # FastAPI app, CORS, lifespan, health check
├── config.py          # Pydantic BaseSettings (all env vars)
├── database.py        # SQLAlchemy 2.0 async engine + session
├── models/            # SQLAlchemy ORM models
├── schemas/           # Pydantic response schemas (mirrors docs/openapi.yaml)
├── ai/                # Azure OpenAI classifier + responder
├── sms/               # Twilio webhook + conversation state machine
└── api/               # REST endpoints for dashboard
```

## Setup

```bash
cp .env.example .env   # fill in credentials
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tables are auto-created on startup via SQLAlchemy `metadata.create_all`.

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/webhooks/sms` | Twilio SMS webhook |
| `GET` | `/api/v1/requests` | List requests (paginated, filterable) |
| `GET` | `/api/v1/requests/{id}` | Request detail with conversation |
| `GET` | `/api/v1/analytics/summary` | KPI summary (totals by status/category) |
| `GET` | `/api/v1/analytics/trend` | Daily request counts |

Full spec: [`docs/openapi.yaml`](../docs/openapi.yaml)

## Key design decisions

- **No LangGraph** — plain Python dict state machine (~80 lines)
- **No Celery/Redis** — `FastAPI BackgroundTasks` + in-memory dict for sessions
- **Structured AI output** — `with_structured_output(ServiceRequest311)`, never raw JSON parsing
- **Always 200 on webhook** — prevents Twilio retries and duplicate reports
- **Phone masking** — full number stored internally, API returns `+1804555****`
