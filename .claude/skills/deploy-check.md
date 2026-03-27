---
description: Railway pre-deployment checklist — environment variables, Twilio webhook URL, database readiness, health checks, and post-deploy smoke tests
---

Run the Railway pre-deployment checklist for the 311 SMS service. Work through every item to catch configuration issues before they cause demo failures.

---

## Step 1: Read current project state

Before running the checklist, read these files:
- `backend/app/config.py` — get all required environment variables from the `Settings` class
- `backend/requirements.txt` — note any recent dependency changes
- `frontend/next.config.ts` — confirm `output: "standalone"` is present
- `docs/openapi.yaml` — confirm spec is current

---

## Step 2: Environment variable checklist

Verify each variable is set in the Railway service dashboard. Variables that cannot be verified from code are marked ⚠️ — provide the exact Railway dashboard path to check.

### Backend service variables

| Variable | Required | Expected format | Notes |
|---|---|---|---|
| `DATABASE_URL` | ✅ | `postgresql+asyncpg://postgres:PASSWORD@db.PROJECTREF.supabase.co:5432/postgres` | asyncpg scheme required |
| `AZURE_OPENAI_ENDPOINT` | ✅ | `https://YOUR-RESOURCE.openai.azure.com/` | Trailing slash required |
| `AZURE_OPENAI_API_KEY` | ✅ | 32-char hex string | From Azure resource → Keys and Endpoint |
| `AZURE_OPENAI_API_VERSION` | ✅ | `2025-01-01-preview` | Or latest stable |
| `AZURE_DEPLOYMENT_CLASSIFIER` | ✅ | `gpt-41-nano` | Must match Azure deployment name exactly |
| `AZURE_DEPLOYMENT_RESPONDER` | ✅ | `gpt-4o-mini` | Must match Azure deployment name exactly |
| `TWILIO_ACCOUNT_SID` | ✅ | `AC...` (34 chars) | From Twilio Console → Account Info |
| `TWILIO_AUTH_TOKEN` | ✅ | 32-char hex string | From Twilio Console → Account Info |
| `TWILIO_PHONE_NUMBER` | ✅ | `+1800...` E.164 format | Toll-free number |
| `FRONTEND_URL` | ✅ | `https://your-frontend.up.railway.app` | No trailing slash; used for CORS |
| `PORT` | Auto | Set by Railway | Do not set manually |

### Frontend service variables

| Variable | Required | Expected format |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ | `https://your-backend.up.railway.app` — no trailing slash |

> **Critical:** `NEXT_PUBLIC_API_URL` must be set **before the build**, not just at runtime. Next.js bakes `NEXT_PUBLIC_*` variables into the bundle at build time. If you update this variable, you must trigger a redeploy.

---

## Step 3: Railway service configuration

Verify in Railway dashboard → Project → each service:

- [ ] Backend service **Root Directory** set to `/backend`
- [ ] Frontend service **Root Directory** set to `/frontend`
- [ ] Backend **health check path** configured: `GET /health`
- [ ] Frontend **health check path** configured: `GET /` (default)
- [ ] Both services are in the **same Railway project** (enables private networking if needed)
- [ ] Railway PostgreSQL add-on added OR Supabase external URL configured in `DATABASE_URL`

---

## Step 4: Twilio webhook configuration

Verify in Twilio Console → Phone Numbers → Active Numbers → select the toll-free number → Messaging:

- [ ] "A message comes in" webhook URL: `https://YOUR-BACKEND.up.railway.app/webhooks/sms`
- [ ] HTTP method: `POST`
- [ ] URL uses **HTTPS** (not HTTP) — Railway provides this automatically
- [ ] No trailing slash on the webhook URL

Common mistake: using the Railway staging URL (`http://`) instead of the production HTTPS URL. Twilio signature validation will fail if the URL scheme doesn't match.

---

## Step 5: Database readiness

- [ ] Supabase project is **active** (not paused — free tier pauses after 1 week of inactivity)
  - Check: Supabase dashboard → Project → if paused, click "Restore project"
- [ ] All 4 tables exist: `service_requests`, `conversations`, `messages`, `request_clusters`
  - Check: Supabase dashboard → Table Editor
- [ ] `DATABASE_URL` uses asyncpg driver: `postgresql+asyncpg://...` not `postgresql://...`
- [ ] pgvector extension enabled if using RAG embeddings: `CREATE EXTENSION IF NOT EXISTS vector;`

---

## Step 6: Code readiness

- [ ] `backend/app/main.py` — FastAPI lifespan event creates tables or Alembic migrations are run
- [ ] `frontend/next.config.ts` — `output: "standalone"` is present
- [ ] `backend/Dockerfile` — uses `$PORT` in CMD: `--port ${PORT:-8000}`
- [ ] `.env` is in `.gitignore` — never committed
- [ ] `docs/openapi.yaml` is current with backend endpoints

---

## Step 7: Post-deploy smoke tests

Run these immediately after Railway finishes deploying. Each should take under 30 seconds.

```bash
BACKEND=https://your-backend.up.railway.app
FRONTEND=https://your-frontend.up.railway.app

# 1. Backend health
curl -s $BACKEND/health
# Expected: {"status": "ok"}

# 2. API responds with valid JSON
curl -s $BACKEND/api/v1/requests | python3 -m json.tool | head -5
# Expected: {"items": [...], "total": N, ...}

# 3. FastAPI docs load (confirms app started cleanly)
curl -s -o /dev/null -w "%{http_code}" $BACKEND/docs
# Expected: 200

# 4. Frontend dashboard loads
curl -s -o /dev/null -w "%{http_code}" $FRONTEND/dashboard
# Expected: 200

# 5. SMS webhook accepts a request
curl -s -X POST $BACKEND/webhooks/sms \
  -d "From=%2B18045550100&Body=test+pothole+on+Broad+St&MessageSid=SMsmoke1"
# Expected: TwiML XML response containing <Message>
```

**Full SMS demo test:** Send a real SMS to the Twilio toll-free number. Should receive AI confirmation reply within 10 seconds.

---

## Step 8: Common failure modes and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Backend 500 on startup | Missing env variable | Railway → backend service → Logs → look for `pydantic_settings` error naming the missing var |
| Twilio receives no webhook reply | Wrong URL or HTTP instead of HTTPS | Twilio Console → Monitor → Logs → check the webhook request log |
| Twilio "Invalid signature" errors | URL mismatch (HTTP vs HTTPS) or wrong auth token | Verify `TWILIO_AUTH_TOKEN` and HTTPS URL; add `X-Forwarded-Proto` handling |
| Frontend shows empty dashboard | `NEXT_PUBLIC_API_URL` not set at build time | Set variable in Railway, then trigger manual redeploy (not just restart) |
| Map page shows blank / broken | Leaflet SSR crash | Verify `dynamic()` import with `ssr: false` in the map page |
| Database connection refused | Supabase paused or wrong URL | Supabase dashboard → resume project; verify asyncpg URL scheme |
| Railway build fails (Node) | Missing `output: "standalone"` | Add to `next.config.ts` and push a new commit |
| Railway build fails (Python) | Missing package in `requirements.txt` | Check build log for import error; add package and push |

---

## When called

1. Execute Step 1 — read the listed files
2. Work through Steps 2–6 line by line — mark ✅ verified from code, ❌ missing/wrong, ⚠️ needs manual verification
3. For ❌ items: provide the exact fix
4. For ⚠️ items: provide the exact Railway or Twilio dashboard path to check
5. Provide the Step 7 smoke test commands with the actual Railway URLs substituted in (if known)
6. End with a go / no-go summary
