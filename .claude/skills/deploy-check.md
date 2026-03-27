---
description: Railway pre-deployment checklist — environment variables, Azure service connectivity, database readiness, health checks, and post-deploy smoke tests
---

Run the Railway pre-deployment checklist for the Procurement Document Processing service. Work through every item to catch configuration issues before they cause demo failures.

---

## Step 1: Read current project state

Before running the checklist, read these files:
- `procurement/backend/app/config.py` — get all required environment variables from the `Settings` class
- `procurement/backend/requirements.txt` — note any recent dependency changes
- `procurement/frontend/next.config.ts` — confirm `output: "standalone"` is present
- `procurement/docs/openapi.yaml` — confirm spec is current

---

## Step 2: Environment variable checklist

### Backend service variables

| Variable | Required | Expected format | Notes |
|---|---|---|---|
| `DATABASE_URL` | yes | `postgresql+asyncpg://postgres:PASSWORD@db.PROJECTREF.supabase.co:5432/postgres` | asyncpg scheme required |
| `AZURE_OPENAI_ENDPOINT` | yes | `https://YOUR-RESOURCE.openai.azure.com/` | Trailing slash required |
| `AZURE_OPENAI_API_KEY` | yes | 32-char hex string | From Azure resource → Keys and Endpoint |
| `AZURE_OPENAI_API_VERSION` | yes | `2025-01-01-preview` | Or latest stable |
| `AZURE_OPENAI_DEPLOYMENT` | yes | `gpt-41-nano` | Must match Azure deployment name exactly |
| `AZURE_BLOB_CONNECTION_STRING` | yes | `DefaultEndpointsProtocol=https;AccountName=...` | From Azure portal → Storage Account → Access Keys |
| `AZURE_BLOB_CONTAINER_NAME` | yes | `procurement-docs` | Container must exist in storage account |
| `AZURE_DOC_INTELLIGENCE_ENDPOINT` | yes | `https://YOUR-RESOURCE.cognitiveservices.azure.com/` | From Azure portal → Document Intelligence resource |
| `AZURE_DOC_INTELLIGENCE_KEY` | yes | 32-char hex string | From Azure portal → Keys and Endpoint |
| `CORS_ORIGINS` | yes | `https://your-frontend.up.railway.app,http://localhost:3000` | Comma-separated |
| `PORT` | Auto | Set by Railway | Do not set manually |

### Frontend service variables

| Variable | Required | Expected format |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | yes | `https://your-backend.up.railway.app` — no trailing slash |

> **Critical:** `NEXT_PUBLIC_API_URL` must be set **before the build**, not just at runtime. Next.js bakes `NEXT_PUBLIC_*` variables into the bundle at build time.

---

## Step 3: Railway service configuration

- [ ] Backend service **Root Directory** set to `procurement/backend`
- [ ] Frontend service **Root Directory** set to `procurement/frontend`
- [ ] Backend **health check path** configured: `GET /health`
- [ ] Frontend **health check path** configured: `GET /` (default)
- [ ] Both services are in the **same Railway project**

---

## Step 4: Azure service readiness

- [ ] Azure Blob Storage container `procurement-docs` exists with access level: None (private)
- [ ] Azure Document Intelligence resource is provisioned (F0 free tier: 500 pages/month)
- [ ] Azure OpenAI `gpt-41-nano` deployment is active and accessible
- [ ] Test connectivity from local machine before deploying

---

## Step 5: Database readiness

- [ ] Supabase project is **active** (not paused)
- [ ] `DATABASE_URL` uses asyncpg driver: `postgresql+asyncpg://...`
- [ ] Tables will be auto-created via FastAPI lifespan event

---

## Step 6: Post-deploy smoke tests

```bash
BACKEND=https://your-backend.up.railway.app
FRONTEND=https://your-frontend.up.railway.app

# 1. Backend health
curl -s $BACKEND/health
# Expected: {"status": "ok"}

# 2. API responds with valid JSON
curl -s $BACKEND/api/v1/documents | python3 -m json.tool | head -5
# Expected: {"items": [...], "total": N, ...}

# 3. FastAPI docs load
curl -s -o /dev/null -w "%{http_code}" $BACKEND/docs
# Expected: 200

# 4. Frontend dashboard loads
curl -s -o /dev/null -w "%{http_code}" $FRONTEND/dashboard
# Expected: 200

# 5. Upload a test PDF
curl -s -X POST $BACKEND/api/v1/documents/upload \
  -F "file=@test.pdf" -w "\n%{http_code}"
# Expected: JSON response + 202 status
```

---

## Step 7: Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Backend 500 on startup | Missing env variable | Check logs for pydantic_settings validation error |
| Upload returns 400 | Invalid file type or size | Check MIME type validation |
| Document stuck in "uploading" | BackgroundTask failed | Check logs for Azure SDK errors |
| OCR returns empty text | Azure DI endpoint/key wrong | Verify credentials in Railway env vars |
| Frontend shows empty dashboard | `NEXT_PUBLIC_API_URL` not set at build time | Set variable, trigger redeploy |
| CORS errors in browser console | Frontend URL not in `CORS_ORIGINS` | Add Railway frontend URL to CORS_ORIGINS |
| Database connection refused | Supabase paused or wrong URL | Resume project, verify asyncpg URL |
