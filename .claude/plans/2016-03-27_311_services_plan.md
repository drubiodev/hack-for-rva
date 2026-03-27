# 311 SMS civic service: full-stack hackathon architecture

**Build an SMS-based 311 system with AI classification, a live operations dashboard, and a map view — all deployable in under 48 hours for ~$65.** The optimal stack pairs Railway (one-click deploy for both services), Supabase (free PostgreSQL + auth + realtime), Azure OpenAI GPT-4.1-nano/GPT-4o-mini (under $2 in tokens for the entire weekend), and Twilio with a toll-free number (avoids the 10–15 day A2P 10DLC registration delay). Every architectural choice below prioritizes time-to-working-demo over theoretical perfection, because at Hack for RVA, the only architecture that matters is the one that runs on stage.

---

## The recommended stack at a glance

| Layer | Technology | Owner | Cost (weekend) |
|---|---|---|---|
| **SMS gateway** | Twilio (toll-free number) | Priyesh | ~$50–55 |
| **Backend API** | Python FastAPI on Railway | Priyesh | $5 |
| **AI classification** | Azure OpenAI GPT-4.1-nano + GPT-4o-mini | Priyesh | ~$1–2 |
| **RAG / embeddings** | text-embedding-3-small + FAISS in-memory | Priyesh | ~$0.04 |
| **Frontend dashboard** | Next.js 16 + shadcn/ui on Railway | Daniel | $0 (shared Railway) |
| **Database** | Supabase Free Tier (PostgreSQL + pgvector) | Shared | $0 |
| **Auth** | Skip (or Supabase Auth if time allows) | Daniel | $0 |
| **Real-time updates** | TanStack Query polling (30s interval) | Daniel | $0 |
| **Session state** | In-memory Python dict (or PostgreSQL) | Priyesh | $0 |
| **Total** | | | **~$58–65** |

The **$200 Azure free trial** (new accounts, 30 days) covers all Azure OpenAI costs with $198+ to spare. Twilio is the largest expense at ~$50–55 (account top-up + messages + toll-free number), and Railway Hobby runs $5/month. The entire weekend comfortably fits under **$70** — well within the $200 budget.

---

## Azure AI: GPT-4.1-nano for classification, GPT-4o-mini for responses

Azure OpenAI Service is the clear winner over Azure AI Foundry's third-party models or direct Anthropic API calls. The reasoning is simple: **GPT-4.1-nano costs $0.10 input / $0.40 output per million tokens** — roughly 10× cheaper than Claude Haiku 3.5 and 3× cheaper than GPT-4o-mini for classification. For 1,000 SMS interactions over the weekend, total token cost is **$0.13**.

Azure AI Foundry (the rebranding of Azure AI Studio, now further evolved into Microsoft Foundry) does offer Claude Sonnet 4.6, Llama 4, Mistral Large 3, and 11,000+ models in its catalog. But third-party Models-as-a-Service models **cannot be purchased with Azure free trial credits** — they require Azure Marketplace billing. Stick with first-party Azure OpenAI models to maximize the $200 trial credit.

**The two-model strategy** optimizes both cost and quality:

- **GPT-4.1-nano** ($0.10/$0.40 per 1M tokens): Handles classification, entity extraction, and category routing. Its 1M-token context window is overkill here but its price-to-performance ratio is unbeatable for structured output tasks.
- **GPT-4o-mini** ($0.15/$0.60 per 1M tokens): Generates human-friendly SMS responses. Proven reliability, vision-capable if you later want image-based reports, and the most battle-tested small model on Azure.

**Skip Azure AI Search entirely.** For a hackathon knowledge base of ~50–100 311 service categories and FAQ entries, an in-memory vector store (FAISS or ChromaDB) with `text-embedding-3-small` embeddings ($0.02/1M tokens) deploys in 30 minutes with zero infrastructure cost. Azure AI Search's free tier is limited to 50MB and 3 indexes — functional but unnecessary complexity for this scale.

The LangChain integration path uses `langchain-openai` (the mature package) rather than the newer `langchain-azure-ai`:

```python
from langchain_openai import AzureChatOpenAI

classifier = AzureChatOpenAI(azure_deployment="gpt-41-nano", temperature=0)
responder = AzureChatOpenAI(azure_deployment="gpt-4o-mini", temperature=0.7)
```

Both packages work, but `langchain-openai` has more community examples and faster debugging when things go wrong at 2 AM during a hackathon.

---

## Railway deploys both services in 5 minutes with zero Docker knowledge

**Railway is the fastest path from `git push` to a running multi-service app.** Its visual project canvas lets you add FastAPI, Next.js, PostgreSQL, and Redis as separate services within a single project, all communicating over automatic private networking. Every service gets automatic HTTPS on `*.up.railway.app` — critical because **Twilio requires HTTPS for webhook URLs**.

Here's how the other platforms compare:

| Platform | Time to deploy | Multi-service networking | HTTPS | Weekend cost | Verdict |
|---|---|---|---|---|---|
| **Railway** | ~5 min | ✅ Built-in private networking | ✅ Auto | $5–10 | **Best for hackathon** |
| Vercel + Railway + Supabase | ~10 min | ❌ Cross-platform CORS | ✅ Auto | $0–5 | Best-of-breed but 3 dashboards |
| Render | ~10 min | ✅ Blueprint IaC | ✅ Auto | $0–20 | Free tier spins down (bad for Twilio) |
| Fly.io | ~15–20 min | ✅ Private networking | ✅ Auto | $1–5 | Requires Docker expertise |
| DigitalOcean App Platform | ~10–15 min | ✅ VPC networking | ✅ Auto | $0 (with $200 credit) | Good but more complex UI |
| Docker Compose on VPS | ~30–60 min | ✅ Docker network | ⚠️ Manual (Caddy) | $0–1 | Maximum control, maximum setup time |

Render's free tier is tempting but its **15-minute spin-down** means Twilio webhooks will hit cold starts of 30–60 seconds — an unacceptable latency for SMS replies. The Vercel + Railway split gives you Vercel's best-in-class Next.js CDN, but managing CORS across two platforms and three dashboards (Vercel, Railway, Supabase) adds cognitive overhead that a 2-person team can't afford.

**Railway setup for the monorepo:**

```
311-sms-service/
├── backend/         → Railway Service 1 (Python, root: /backend)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
├── frontend/        → Railway Service 2 (Node, root: /frontend)
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── docker-compose.yml   → Local dev only
└── .env.example
```

Each service points to its subdirectory via Railway's "Root Directory" setting. Add PostgreSQL with one click on the canvas. Services reference each other via `backend.railway.internal:8000` on the private network. Total deployment time: connect GitHub repo → create project → add 2 services + set root directories → add PostgreSQL → set environment variables → deploy. **Five minutes, no Docker knowledge required** (Railway auto-detects Python and Node via Nixpacks).

---

## Priyesh's backend: FastAPI monolith with structured AI output

The backend architecture optimizes for one engineer building everything in ~24 working hours. **Skip LangGraph** — a simple Python state machine with LangChain's `with_structured_output()` is faster to build, easier to debug, and covers 90% of the conversational SMS workflow.

**Project structure:**

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router mounting
│   ├── config.py            # Pydantic BaseSettings for all env vars
│   ├── database.py          # SQLAlchemy 2.0 async engine + session
│   ├── models/              # SQLAlchemy models
│   │   ├── service_request.py
│   │   └── conversation.py
│   ├── schemas/             # Pydantic request/response schemas
│   ├── sms/                 # Twilio webhook + SMS processing
│   │   ├── router.py        # POST /webhooks/sms
│   │   ├── service.py       # Conversation state machine
│   │   └── twilio_utils.py  # Signature validation, send SMS
│   ├── ai/                  # LangChain integration
│   │   ├── classifier.py    # Structured output extraction
│   │   └── prompts.py       # System prompts
│   └── api/                 # Dashboard REST endpoints
│       └── router.py        # GET/PATCH /api/v1/requests
├── requirements.txt
└── Dockerfile
```

The **core AI integration** uses LangChain's `with_structured_output()` — one of the most powerful features for this use case. It forces the LLM to return a validated Pydantic model:

```python
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI

class ServiceRequest311(BaseModel):
    category: str = Field(description="pothole, streetlight, graffiti, trash, water, sidewalk, noise, other")
    location: str = Field(description="Street address or intersection, 'unknown' if not mentioned")
    description: str = Field(description="One-sentence summary of the issue")
    urgency: str = Field(description="low, medium, or high")

classifier = AzureChatOpenAI(azure_deployment="gpt-41-nano", temperature=0)
structured_classifier = classifier.with_structured_output(ServiceRequest311)

# Returns a validated Pydantic object — no JSON parsing errors, no hallucinated fields
result = await structured_classifier.ainvoke("There's a huge pothole on 5th and Main")
```

The **SMS conversation state machine** avoids LangGraph entirely — just a Python dict keyed by phone number:

```python
sessions: dict[str, dict] = {}

async def process_sms(phone: str, message: str) -> str:
    session = sessions.get(phone)
    if not session:
        request = await structured_classifier.ainvoke(message)
        sessions[phone] = {"step": "confirm", "data": request.model_dump()}
        return f"Got it: {request.category} at {request.location}. Reply YES to confirm."
    elif session["step"] == "confirm":
        if "yes" in message.lower():
            await save_to_db(session["data"])
            del sessions[phone]
            return "Submitted! Reference #12345. We'll update you via text."
        del sessions[phone]
        return "Cancelled. Text us anytime."
```

This covers the MVP flow: citizen texts a report → AI extracts category/location/urgency → asks for confirmation → saves to database. The entire AI + conversation layer is **~80 lines of Python**.

**Key packages** (pin these in requirements.txt):

```
fastapi[standard]>=0.135.0
uvicorn[standard]
sqlalchemy[asyncio]>=2.0
asyncpg
alembic
twilio>=9.10.0
langchain-openai
langchain-core
python-multipart
python-dotenv
pydantic-settings
```

The Twilio webhook validates signatures, processes the SMS through the AI pipeline, and returns TwiML XML — all in a single async endpoint. Use `FastAPI BackgroundTasks` for non-blocking database writes and outbound SMS; skip Celery entirely.

**Database layer:** SQLAlchemy 2.0 async with asyncpg connects directly to Supabase's PostgreSQL via the standard connection string. Use Alembic with the async template for migrations. For the hackathon, a shortcut: `Base.metadata.create_all()` in the FastAPI lifespan event skips Alembic setup entirely.

---

## Daniel's frontend: Next.js 16 dashboard in shadcn/ui

The frontend uses **Next.js 16** (latest stable as of March 2026, requires React 19), **shadcn/ui** for all UI components, **TanStack Table** for sortable data grids, **React-Leaflet** for the map, and **TanStack Query** for data fetching with auto-polling.

**Scaffold in 30 minutes:**

```bash
npx create-next-app@latest dashboard --typescript --tailwind --app
cd dashboard
npx shadcn@latest init
npx shadcn@latest add sidebar table card badge dialog select tabs chart button input skeleton
npm install @tanstack/react-query @tanstack/react-table react-leaflet leaflet
```

**Dashboard pages** (priority order for the 48 hours):

| Page | Route | Key components | Build time |
|---|---|---|---|
| Dashboard overview | `/dashboard` | KPI cards, category bar chart, recent requests | 3–4 hrs |
| Request list | `/dashboard/requests` | TanStack Table + shadcn DataTable, filters, badges | 3–4 hrs |
| Map view | `/dashboard/map` | React-Leaflet with request pins | 2–3 hrs |
| Request detail | `/dashboard/requests/[id]` | Status card, conversation history, map pin | 2 hrs |
| Analytics | `/dashboard/analytics` | shadcn/ui Charts (Recharts-based) | 2 hrs |

**Real-time updates via polling** — the simplest approach that works perfectly for a dashboard:

```tsx
const { data: requests } = useQuery({
  queryKey: ["requests"],
  queryFn: () => fetch(`${API_URL}/api/v1/requests`).then(r => r.json()),
  refetchInterval: 30_000, // Auto-refresh every 30 seconds
})
```

That's one line of configuration. No WebSocket setup, no SSE, no additional backend infrastructure. TanStack Query handles caching, loading states, error handling, and background refetching automatically.

**React-Leaflet requires a dynamic import** to avoid SSR crashes (Leaflet accesses `window` directly):

```tsx
const Map = dynamic(() => import("@/components/LeafletMap"), {
  ssr: false,
  loading: () => <div className="h-[600px] animate-pulse bg-muted rounded-xl" />,
})
```

OpenStreetMap tiles are free with no API key — **Richmond, VA center coordinates: [37.5407, -77.4360]**.

**Skip authentication** for the hackathon demo. If judges ask about it, mention that Supabase Auth (50,000 MAU free tier) slots in with ~2 hours of work post-hackathon. Spending 4+ hours on auth during a 48-hour sprint is a poor allocation of Daniel's time versus building the map view and analytics that will wow judges.

For deployment, add `output: "standalone"` to `next.config.ts` so Railway can build a minimal Docker image (~200MB instead of 2GB+).

---

## Database schema and infrastructure decisions

**Supabase Free Tier** provides 500MB PostgreSQL, pgvector pre-installed, 50,000 auth MAUs, realtime subscriptions, and edge functions — all at zero cost. FastAPI connects via the standard PostgreSQL connection string (`postgresql+asyncpg://postgres:PASSWORD@db.PROJECTREF.supabase.co:5432/postgres`). Any data written by FastAPI automatically triggers Supabase Realtime events that the Next.js frontend can subscribe to if you upgrade from polling later.

**Skip Redis entirely.** For ~500 SMS conversations, PostgreSQL handles session state trivially (sub-5ms queries with indexing). The in-memory Python dict approach is even simpler for the hackathon — the only risk is losing conversation state on backend restart, which is acceptable for a demo.

**Core schema** (4 tables for the MVP):

```sql
CREATE TABLE service_requests (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    address TEXT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    status VARCHAR(50) DEFAULT 'new',     -- new/open/in_progress/resolved
    priority VARCHAR(20) DEFAULT 'medium', -- low/medium/high/urgent
    ai_confidence DECIMAL(5,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    service_request_id INTEGER REFERENCES service_requests(id),
    status VARCHAR(30) DEFAULT 'active',
    current_step VARCHAR(50),
    context JSONB DEFAULT '{}',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_message_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    direction VARCHAR(10) NOT NULL,  -- inbound/outbound
    body TEXT NOT NULL,
    twilio_sid VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE request_clusters (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100),
    centroid_lat DECIMAL(10,8),
    centroid_lng DECIMAL(11,8),
    request_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Add pgvector's `embedding VECTOR(1536)` column to `service_requests` only if you implement RAG for similar-request detection — it's a stretch goal, not an MVP feature.

---

## Twilio: use a toll-free number, not 10DLC

**A2P 10DLC campaign registration takes 10–15 business days** — far longer than the hackathon allows. A **toll-free number** ($2.15/month) with toll-free verification (free, processed in hours to days) avoids this entirely and lets you send to any US phone number from day one.

Two viable Twilio strategies:

- **Budget demo ($0):** Twilio trial account with ~$15.50 preloaded credits. Limitation: can only message **pre-verified phone numbers** (add judges' phones manually), and all outbound messages get a "Sent from Twilio trial" prefix. Good enough if judges are the only audience.
- **Full demo (~$55):** Upgrade to paid account ($20 minimum top-up), buy toll-free number ($2.15), send to any US number. At ~$0.01/message, 3,000 messages costs ~$30. This is the recommended path for a convincing demo.

**Webhook configuration:** In Twilio Console → Phone Numbers → select number → Messaging → set webhook URL to `https://your-backend.up.railway.app/webhooks/sms` (POST). Railway's automatic HTTPS means this works immediately with no SSL configuration.

---

## Complete budget breakdown

| Item | Cost | Notes |
|---|---|---|
| Azure OpenAI tokens (GPT-4.1-nano + GPT-4o-mini) | ~$1–2 | Covered by $200 free trial credit |
| Azure free trial remaining credit | $198+ | Unused, available for 30 days |
| Twilio account top-up | $20 | Minimum to upgrade from trial |
| Twilio toll-free number | $2.15 | Monthly |
| Twilio SMS (~3,000 messages) | $30–35 | ~$0.01/msg including carrier fees |
| Railway Hobby plan | $5 | Includes $5 usage credits |
| Supabase (PostgreSQL + Auth) | $0 | Free tier |
| Redis | $0 | Skipped — not needed |
| Domain name | $0 | Railway provides .up.railway.app |
| **Total** | **~$58–65** | **$135+ remaining from $200 budget** |

---

## 48-hour build timeline

**Priyesh (Backend — Hours 0–48):**

| Hours | Task |
|---|---|
| 0–2 | Scaffold FastAPI app, config, database connection, deploy to Railway |
| 2–5 | Twilio webhook endpoint, signature validation, basic TwiML response |
| 5–10 | Azure OpenAI integration, structured output classifier, SMS response generation |
| 10–16 | REST API endpoints for dashboard (GET requests, PATCH status, GET analytics) |
| 16–22 | Multi-turn conversation state machine, session management |
| 22–30 | RAG with FAISS + embeddings for category knowledge base (stretch) |
| 30–40 | Request clustering, priority scoring, edge cases, error handling |
| 40–48 | Integration testing, demo prep, load testing with Twilio |

**Daniel (Frontend — Hours 0–48):**

| Hours | Task |
|---|---|
| 0–2 | Scaffold Next.js 16 + shadcn/ui + TanStack Query, deploy to Railway |
| 2–6 | Dashboard layout with shadcn Sidebar, KPI cards, overview page |
| 6–12 | DataTable for request list with sorting, filtering, status badges |
| 12–18 | Map view with React-Leaflet, request pins, popups |
| 18–24 | Request detail page, conversation history display |
| 24–32 | Analytics page with charts (category breakdown, trends, response times) |
| 32–40 | Real-time polling, mobile responsive, dark mode toggle |
| 40–48 | Polish, demo flow, loading states, empty states |

**Critical path:** Priyesh must have the Twilio webhook + AI classifier working by hour 10 so Daniel can start fetching real data by hour 12. The first cross-team integration point is `GET /api/v1/requests` — agree on the JSON response shape in hour 0 and mock it immediately.

## Conclusion

The architecture makes three non-obvious bets that save the most time. First, **GPT-4.1-nano for classification at $0.10/1M tokens** makes AI costs essentially free, removing any need to optimize prompts for cost during the hackathon. Second, **skipping LangGraph in favor of an 80-line Python state machine** eliminates an entire framework's learning curve while delivering identical functionality for the demo. Third, **Railway's one-project multi-service canvas** means both engineers deploy independently from the same repo without coordinating infrastructure. The total cost of ~$65 leaves over $135 of the $200 budget unspent — enough headroom to experiment with GPT-4o for higher-quality responses or spin up additional services if the demo scope expands.