# 311 SMS Civic Service — Technical Implementation Plan

**Project:** HackathonRVA 2026 — SMS-based 311 civic reporting system
**Team:** Priyesh (backend), Daniel (frontend)
**Timeline:** 48 hours | **Budget:** ~$65

---

## 1. System Architecture Overview

### Component Diagram

```
                          ┌──────────────────────────────────────────────────┐
                          │              Railway Project                     │
                          │                                                  │
┌──────────┐    HTTPS     │  ┌─────────────────────┐    Private Net         │
│  Twilio  │─────────────────▶  FastAPI Backend     │◄──────────────┐       │
│  (SMS)   │◄────TwiML────│  │  (Python 3.12)      │               │       │
└──────────┘              │  │                      │               │       │
                          │  │  /webhooks/sms       │     ┌─────────┴─────┐ │
┌──────────┐    HTTPS     │  │  /api/v1/*           │     │  Next.js 16   │ │
│ Citizens │──SMS──▶ Twilio│  │  /health             │     │  Dashboard    │ │
└──────────┘              │  └──────┬───────┬───────┘     │  (shadcn/ui)  │ │
                          │         │       │              └───────────────┘ │
┌──────────┐              │         │       │                                │
│  Judges  │──Browser─────│─────────│───────│──────────▶ Next.js Dashboard  │
│  / Ops   │              │         │       │                                │
└──────────┘              │         ▼       ▼                                │
                          │  ┌──────────┐ ┌────────────────┐                │
                          │  │ Supabase │ │ Azure OpenAI   │ (external)     │
                          │  │ Postgres │ │ GPT-4.1-nano   │                │
                          │  │ (free)   │ │ GPT-4o-mini    │                │
                          │  └──────────┘ └────────────────┘                │
                          └──────────────────────────────────────────────────┘
```

### Data Flow

1. **Citizen** sends SMS to Twilio toll-free number
2. **Twilio** POSTs webhook to `POST /webhooks/sms` on Railway backend
3. **FastAPI** validates Twilio signature, extracts `From` + `Body`
4. **SMS service** checks in-memory session dict for conversation state
5. **AI classifier** (GPT-4.1-nano via `with_structured_output`) extracts category, location, urgency
6. **Responder** (GPT-4o-mini) generates human-friendly SMS reply
7. **Backend** returns TwiML XML; Twilio delivers reply to citizen
8. **Service request** saved to Supabase PostgreSQL via async SQLAlchemy
9. **Dashboard** (Next.js) polls `GET /api/v1/requests` every 30s via TanStack Query
10. **Ops user** views requests on map, filters by status/category, reviews analytics

### Deployment Topology

| Service | Platform | URL Pattern | Root Dir |
|---|---|---|---|
| Backend (FastAPI) | Railway | `backend-*.up.railway.app` | `/backend` |
| Frontend (Next.js) | Railway | `frontend-*.up.railway.app` | `/frontend` |
| Database | Supabase | `db.PROJECTREF.supabase.co:5432` | N/A |
| AI Models | Azure OpenAI | `*.openai.azure.com` | N/A |
| SMS Gateway | Twilio | N/A (webhook inbound) | N/A |

---

## 2. Backend Task Breakdown

| ID | Task | Description | Dependencies | Effort | Acceptance Criteria |
|---|---|---|---|---|---|
| **BE-01** | Project scaffold | Create `/backend` with FastAPI app, `requirements.txt`, `Dockerfile`, directory structure (`app/`, `app/models/`, `app/schemas/`, `app/sms/`, `app/ai/`, `app/api/`) | None | 1 hr | `uvicorn app.main:app` starts; `GET /health` returns `{"status":"ok"}` |
| **BE-02** | Config & settings | `app/config.py` with Pydantic `BaseSettings`: DATABASE_URL, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, TWILIO_PHONE_NUMBER, CORS_ORIGINS | BE-01 | 0.5 hr | All env vars loaded from `.env`; missing required vars raise validation error on startup |
| **BE-03** | Database models | SQLAlchemy 2.0 async models for `service_requests`, `conversations`, `messages`; async engine + session factory in `app/database.py`; table auto-creation in FastAPI lifespan | BE-02 | 1.5 hr | Tables created in Supabase on app startup; models importable and usable in async context |
| **BE-04** | Pydantic schemas | Request/response schemas matching `docs/openapi.yaml`: `ServiceRequestOut`, `ServiceRequestList`, `AnalyticsSummary`, `AnalyticsTrend`, `TrendPoint` | BE-03 | 1 hr | Schemas serialize SQLAlchemy models correctly; phone numbers masked in output |
| **BE-05** | AI classifier | `app/ai/classifier.py` using `AzureChatOpenAI(azure_deployment="gpt-41-nano")` with `with_structured_output(ServiceRequest311)` to extract category, location, description, urgency | BE-02 | 2 hr | Given "pothole on 5th and Main", returns structured object with `category="pothole"`, `location="5th and Main"` |
| **BE-06** | AI responder | `app/ai/prompts.py` with system prompts; GPT-4o-mini generates citizen-friendly SMS replies based on extracted data and conversation state | BE-05 | 1.5 hr | Generated replies are under 160 chars, reference the category and location, and include a reference number |
| **BE-07** | SMS state machine | `app/sms/service.py` with in-memory `sessions: dict[str, dict]`; states: `initial` -> `confirm` -> `done`; handles YES/NO confirmation, cancellation, STATUS queries | BE-05, BE-06 | 2 hr | Full conversation flow works: report -> confirm -> save. STATUS query returns latest request status. Session cleaned up after completion |
| **BE-08** | Twilio webhook | `app/sms/router.py`: `POST /webhooks/sms` accepts form data (`From`, `Body`, `MessageSid`), validates Twilio signature, processes through state machine, returns TwiML XML. Always returns 200 | BE-07 | 2 hr | Twilio signature validated; valid TwiML returned for all inputs including errors; Twilio can successfully deliver replies |
| **BE-09** | REST API — list requests | `GET /api/v1/requests` with query params: `status`, `category`, `limit`, `offset`. Returns paginated `ServiceRequestList` | BE-04 | 1.5 hr | Pagination works; filters apply correctly; total count is accurate; response matches OpenAPI spec |
| **BE-10** | REST API — request detail | `GET /api/v1/requests/{id}` returns single `ServiceRequest` with conversation messages | BE-04 | 1 hr | Returns 404 for missing ID; includes full request data; response matches OpenAPI spec |
| **BE-11** | REST API — analytics summary | `GET /api/v1/analytics/summary` returns total count, breakdown by status and category | BE-04 | 1 hr | Counts are accurate; all categories/statuses represented; empty database returns zeroes |
| **BE-12** | REST API — analytics trend | `GET /api/v1/analytics/trend` with `days` param returns daily request counts | BE-04 | 1 hr | Returns array of `{date, count}` objects for specified range; defaults to 7 days |
| **BE-13** | Background tasks | Use `FastAPI BackgroundTasks` for: saving messages to DB after TwiML response, geocoding addresses (stretch) | BE-08 | 1 hr | Webhook response time under 1s; DB writes happen asynchronously; errors logged but don't crash |
| **BE-14** | Phone masking | Mask phone numbers in API responses: `+1804555****` | BE-04 | 0.5 hr | No full phone numbers exposed via REST API; Twilio webhook still uses full numbers internally |

---

## 3. Frontend Task Breakdown

| ID | Task | Description | Dependencies | Effort | Acceptance Criteria |
|---|---|---|---|---|---|
| **FE-01** | Project scaffold | `npx create-next-app@latest` with TypeScript, Tailwind, App Router; install shadcn/ui, TanStack Query, TanStack Table, react-leaflet, leaflet | None | 1 hr | Dev server runs; shadcn components render; TanStack QueryProvider wraps app |
| **FE-02** | API layer & types | `src/lib/types.ts` mirroring OpenAPI schemas; `src/lib/api.ts` with typed fetch functions for all endpoints; `NEXT_PUBLIC_API_URL` config | FE-01 | 1.5 hr | All API functions typed; types match `docs/openapi.yaml` exactly; API base URL configurable |
| **FE-03** | Dashboard layout | App shell with shadcn Sidebar: nav links for Overview, Requests, Map, Analytics; responsive header; `output: "standalone"` in next.config | FE-01 | 2 hr | Sidebar navigates between pages; layout responsive on mobile; standalone build works |
| **FE-04** | Dashboard overview | `/dashboard` page: KPI cards (total requests, new, in progress, resolved), category bar chart (shadcn/Recharts), recent requests table (5 most recent) | FE-02, FE-03 | 3 hr | Cards show correct counts from `/analytics/summary`; chart renders category breakdown; recent list links to detail |
| **FE-05** | Request list page | `/dashboard/requests`: TanStack Table with columns (ID, category, location, status, urgency, date); sortable headers; status/category filter dropdowns; pagination | FE-02, FE-03 | 3 hr | Table sorts by all columns; filters update URL params and refetch; pagination controls work; status badges color-coded |
| **FE-06** | Request detail page | `/dashboard/requests/[id]`: status card with badge, description, location, map pin (single marker), conversation message history, status update action | FE-02, FE-03 | 2 hr | All fields display; conversation messages show direction (inbound/outbound); 404 state for missing requests |
| **FE-07** | Map page | `/dashboard/map`: React-Leaflet with OpenStreetMap tiles, centered on Richmond VA (37.5407, -77.4360); request markers with category-colored pins; click popup with summary + link to detail | FE-02, FE-03 | 2.5 hr | Map renders without SSR crash (dynamic import); markers positioned correctly; popups show request info; no API key needed |
| **FE-08** | Analytics page | `/dashboard/analytics`: daily trend line chart, category pie chart, status distribution, average response time card | FE-02, FE-03 | 2 hr | Charts render with data from `/analytics/summary` and `/analytics/trend`; handles empty data gracefully |
| **FE-09** | Polling setup | TanStack Query `refetchInterval: 30_000` on list, detail, and analytics queries; loading skeletons during fetch; stale-while-revalidate | FE-02 | 1 hr | Data auto-refreshes every 30s; no flicker on refetch; loading skeleton on initial load; error state on failure |
| **FE-10** | Polish & responsive | Mobile-responsive tables (horizontal scroll), dark mode toggle, empty states, loading skeletons for all pages | FE-03 | 2 hr | Dashboard usable on mobile; dark/light mode toggle works; empty states display meaningful messages |

---

## 4. Integration Tasks

| ID | Task | Description | Dependencies | Effort | Acceptance Criteria |
|---|---|---|---|---|---|
| **INT-01** | CORS configuration | Backend: add frontend Railway URL + `localhost:3000` to `CORS_ORIGINS`; Frontend: ensure API calls include correct headers | BE-01, FE-01 | 0.5 hr | Frontend can call backend APIs from both local dev and Railway deployment without CORS errors |
| **INT-02** | OpenAPI contract sync | Verify `docs/openapi.yaml` matches implemented endpoints; frontend types match spec; run manual smoke test on each endpoint | BE-09 thru BE-12, FE-02 | 1 hr | All endpoints return responses matching OpenAPI schemas; TypeScript types have no mismatches |
| **INT-03** | Railway deployment | Configure Railway project with two services (backend root: `/backend`, frontend root: `/frontend`); set all environment variables; verify auto-HTTPS and private networking | BE-01, FE-01 | 1 hr | Both services deploy from `git push`; HTTPS endpoints accessible; health check passes |
| **INT-04** | Twilio webhook config | Set Twilio messaging webhook URL to Railway backend `POST /webhooks/sms`; test end-to-end SMS flow | BE-08, INT-03 | 0.5 hr | SMS sent to Twilio number triggers webhook; AI processes message; reply delivered to phone |
| **INT-05** | End-to-end smoke tests | Test full flow: SMS -> AI classification -> DB save -> dashboard display -> map pin -> analytics update | INT-01 thru INT-04 | 1.5 hr | Complete citizen journey works; dashboard reflects new request within 30s; map shows new pin |

---

## 5. Architecture Decision Records (ADRs)

### ADR-01: No LangGraph — Plain Dict State Machine

**Status:** Accepted
**Context:** LangGraph provides structured state machines for LLM workflows but adds framework overhead, a learning curve, and debugging complexity.
**Decision:** Use a plain Python dictionary keyed by phone number (`sessions: dict[str, dict]`) with explicit state transitions (`initial` -> `confirm` -> `done`).
**Consequences:** ~80 lines of Python covers the entire SMS conversation flow. No framework dependency. State is trivially inspectable via debugger. Trade-off: no built-in persistence or replay — acceptable for a demo.

### ADR-02: No Celery/Redis — FastAPI BackgroundTasks + In-Memory Dict

**Status:** Accepted
**Context:** Celery + Redis is the standard async task queue for Python but requires two additional services (Redis broker, Celery worker) and significant setup time.
**Decision:** Use `FastAPI BackgroundTasks` for async DB writes after returning TwiML. Use an in-memory Python dict for SMS session state.
**Consequences:** Zero additional infrastructure. Webhook response time stays under 1s. Trade-off: session state lost on backend restart — acceptable for 48-hour demo. If needed post-hackathon, sessions can be moved to PostgreSQL with minimal refactoring.

### ADR-03: No WebSockets/SSE — TanStack Query 30s Polling

**Status:** Accepted
**Context:** Real-time dashboard updates could use WebSockets, SSE, or polling. WebSockets require backend state management; SSE requires connection pooling.
**Decision:** TanStack Query's `refetchInterval: 30_000` provides auto-polling with one line of config.
**Consequences:** Dashboard data is at most 30s stale — well within acceptable limits for a 311 operations dashboard. Zero backend infrastructure for real-time. TanStack Query handles caching, deduplication, and background refetching automatically.

### ADR-04: Leaflet Dynamic Import

**Status:** Accepted
**Context:** Leaflet accesses `window` directly, causing SSR crashes in Next.js.
**Decision:** Use `next/dynamic` with `ssr: false` to load the map component client-side only. OpenStreetMap tiles (free, no API key).
**Consequences:** Map renders correctly in both dev and production. Small loading skeleton shown during client-side hydration. No map tile API costs.

### ADR-05: Standalone Next.js Output

**Status:** Accepted
**Context:** Default Next.js builds include the full `node_modules` directory, resulting in 2GB+ Docker images.
**Decision:** Set `output: "standalone"` in `next.config.ts` to produce a minimal self-contained build.
**Consequences:** Docker image ~200MB instead of 2GB+. Faster Railway deploys. Slightly different static file serving (handled by Railway).

### ADR-06: Skip Authentication

**Status:** Accepted
**Context:** Implementing auth (even with Supabase Auth) costs 4+ hours for zero demo value.
**Decision:** No auth for the hackathon. Dashboard is publicly accessible.
**Consequences:** Faster development. If judges ask, we mention Supabase Auth (50k MAU free tier) as a 2-hour post-hackathon addition.

---

## 6. Environment Variables

### Backend (`/backend/.env`)

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | Supabase PostgreSQL connection string | `postgresql+asyncpg://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource endpoint | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | `sk-...` |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version | `2024-12-01-preview` |
| `AZURE_OPENAI_CLASSIFIER_DEPLOYMENT` | GPT-4.1-nano deployment name | `gpt-41-nano` |
| `AZURE_OPENAI_RESPONDER_DEPLOYMENT` | GPT-4o-mini deployment name | `gpt-4o-mini` |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | `your_auth_token` |
| `TWILIO_PHONE_NUMBER` | Twilio toll-free number | `+18005551234` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `https://frontend-xxx.up.railway.app,http://localhost:3000` |
| `ENVIRONMENT` | Runtime environment | `production` or `development` |

### Frontend (`/frontend/.env.local`)

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `https://backend-xxx.up.railway.app` |
| `NEXT_PUBLIC_MAP_CENTER_LAT` | Map default latitude | `37.5407` |
| `NEXT_PUBLIC_MAP_CENTER_LNG` | Map default longitude | `-77.4360` |

---

## 7. Database Schema

```sql
-- Core service requests from citizens
CREATE TABLE service_requests (
    id SERIAL PRIMARY KEY,
    reference_number VARCHAR(20) UNIQUE NOT NULL,  -- e.g., "RVA-2026-00042"
    phone_number VARCHAR(20) NOT NULL,             -- full number (masked in API responses)
    category VARCHAR(50) NOT NULL,                 -- pothole|streetlight|graffiti|trash|water|sidewalk|noise|other
    description TEXT NOT NULL,
    location TEXT,                                  -- free-text address or intersection
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    urgency INTEGER NOT NULL DEFAULT 3 CHECK (urgency BETWEEN 1 AND 5),
    status VARCHAR(20) NOT NULL DEFAULT 'new',     -- new|in_progress|resolved
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_category ON service_requests(category);
CREATE INDEX idx_service_requests_created_at ON service_requests(created_at DESC);

-- SMS conversation sessions (persisted for history; active state in memory)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    service_request_id INTEGER REFERENCES service_requests(id),
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active|completed|cancelled
    current_step VARCHAR(50),                       -- initial|confirm|done
    context JSONB DEFAULT '{}',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_phone ON conversations(phone_number);

-- Individual SMS messages (inbound and outbound)
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    direction VARCHAR(10) NOT NULL,                -- inbound|outbound
    body TEXT NOT NULL,
    twilio_sid VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
```

---

## 8. Dependency Graph

```
BE-01 (scaffold)
 ├── BE-02 (config)
 │    ├── BE-03 (models) ── BE-04 (schemas)
 │    │                      ├── BE-09 (list API)
 │    │                      ├── BE-10 (detail API)
 │    │                      ├── BE-11 (analytics summary)
 │    │                      ├── BE-12 (analytics trend)
 │    │                      └── BE-14 (phone masking)
 │    ├── BE-05 (classifier)
 │    │    ├── BE-06 (responder)
 │    │    └── BE-07 (state machine) ── BE-08 (webhook) ── BE-13 (bg tasks)
 │    │
FE-01 (scaffold)
 ├── FE-02 (API layer) ── FE-09 (polling)
 ├── FE-03 (layout) ── FE-10 (polish)
 │    ├── FE-04 (overview)
 │    ├── FE-05 (request list)
 │    ├── FE-06 (request detail)
 │    ├── FE-07 (map)
 │    └── FE-08 (analytics)

INT-01 (CORS) ── requires BE-01, FE-01
INT-02 (contract sync) ── requires BE-09..12, FE-02
INT-03 (Railway deploy) ── requires BE-01, FE-01
INT-04 (Twilio config) ── requires BE-08, INT-03
INT-05 (e2e smoke) ── requires INT-01..04
```

### Suggested Execution Order

**Phase 1 — Foundations (Hours 0-4)**
- Parallel: BE-01, BE-02, FE-01
- Then: BE-03, FE-02, FE-03

**Phase 2 — Core Features (Hours 4-14)**
- Priyesh: BE-05 -> BE-06 -> BE-07 -> BE-08 (AI + SMS pipeline)
- Daniel: FE-04 -> FE-05 (dashboard + request list)
- Integration: INT-01 (CORS), INT-03 (Railway deploy)

**Phase 3 — API + Dashboard (Hours 14-24)**
- Priyesh: BE-04 -> BE-09 -> BE-10 -> BE-11 -> BE-12 -> BE-14
- Daniel: FE-06 -> FE-07 (detail + map)
- Integration: INT-04 (Twilio webhook config)

**Phase 4 — Polish + Integration (Hours 24-40)**
- Priyesh: BE-13 (background tasks), edge cases, error handling
- Daniel: FE-08 -> FE-09 -> FE-10 (analytics, polling, polish)
- Integration: INT-02 (contract sync)

**Phase 5 — Demo Prep (Hours 40-48)**
- Integration: INT-05 (e2e smoke tests)
- Both: demo flow rehearsal, final bug fixes

**Critical path:** BE-01 -> BE-02 -> BE-05 -> BE-07 -> BE-08 -> INT-04 (SMS works end-to-end by hour ~14)
