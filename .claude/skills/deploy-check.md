---
description: Azure Container Apps pre-deployment checklist — environment variables, Azure service connectivity, database readiness, health checks, and post-deploy smoke tests
---

Run the Azure Container Apps pre-deployment checklist for the Procurement Document Processing service. Work through every item to catch configuration issues before they cause demo failures.

---

## Step 1: Read current project state

Before running the checklist, read these files:
- `procurement/backend/app/config.py` — get all required environment variables from the `Settings` class
- `procurement/backend/requirements.txt` — note any recent dependency changes
- `procurement/frontend/next.config.ts` — confirm `output: "standalone"` is present
- `procurement/docs/openapi.yaml` — confirm spec is current

---

## Step 2: Environment variable checklist

### Backend container variables

| Variable | Required | Expected format | Notes |
|---|---|---|---|
| `DATABASE_URL` | yes | `postgresql+asyncpg://user:pass@server.postgres.database.azure.com:5432/procurement?ssl=require` | asyncpg scheme + SSL required for Azure |
| `AZURE_OPENAI_ENDPOINT` | yes | `https://YOUR-RESOURCE.openai.azure.com/` | Trailing slash required |
| `AZURE_OPENAI_KEY` | yes | 32-char hex string | From Azure resource → Keys and Endpoint |
| `AZURE_OPENAI_API_VERSION` | yes | `2024-12-01-preview` | Or latest stable |
| `AZURE_OPENAI_DEPLOYMENT` | yes | `chatgpt-5.4-mini` | Must match Azure deployment name exactly |
| `AZURE_BLOB_CONNECTION_STRING` | yes | `DefaultEndpointsProtocol=https;AccountName=...` | From Azure portal → Storage Account → Access Keys |
| `AZURE_BLOB_CONTAINER_NAME` | yes | `procurement-docs` | Container must exist in storage account |
| `AZURE_DI_ENDPOINT` | yes | `https://YOUR-RESOURCE.cognitiveservices.azure.com/` | From Azure portal → Document Intelligence resource |
| `AZURE_DI_KEY` | yes | 32-char hex string | From Azure portal → Keys and Endpoint |
| `AZURE_SEARCH_ENDPOINT` | yes | `https://YOUR-RESOURCE.search.windows.net` | From Azure portal → AI Search resource |
| `AZURE_SEARCH_KEY` | yes | Admin key | From Azure portal → Keys |
| `AZURE_SEARCH_INDEX` | yes | `procurement-docs` | Index name for RAG chatbot |
| `CORS_ORIGINS` | yes | `https://frontend-aca-fqdn,http://localhost:3000` | Comma-separated, include ACA frontend FQDN |
| `ENVIRONMENT` | yes | `production` | Set to production in ACA |

### Frontend container variables

| Variable | Required | Expected format |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | yes | `https://backend-aca-fqdn` — no trailing slash |

> **Critical:** `NEXT_PUBLIC_API_URL` must be set as a **build arg** during Docker build. Next.js bakes `NEXT_PUBLIC_*` variables into the bundle at build time: `docker build --build-arg NEXT_PUBLIC_API_URL=https://... .`

---

## Step 3: Azure Container Apps configuration

- [ ] Azure Container Registry (Basic tier) provisioned
- [ ] Container Apps Environment created
- [ ] Backend Container App deployed with correct image from ACR
- [ ] Frontend Container App deployed with correct image from ACR
- [ ] Backend **health check path** configured: `GET /health`
- [ ] Both Container Apps in the **same environment**
- [ ] Min replicas = 1 on both apps (avoid cold start during demo)

---

## Step 4: Azure service readiness

- [ ] Azure Blob Storage container `procurement-docs` exists with access level: None (private)
- [ ] Azure Document Intelligence resource is provisioned (F0 free tier: 500 pages/month)
- [ ] Azure OpenAI `chatgpt-5.4-mini` deployment is active and accessible
- [ ] Azure AI Search resource provisioned (Free tier: 1 index, 50MB)
- [ ] Azure AI Search index `procurement-docs` created
- [ ] Test connectivity from local machine before deploying

---

## Step 5: Database readiness

- [ ] Azure PostgreSQL Flexible Server provisioned (Burstable B1ms)
- [ ] Firewall allows Azure services access
- [ ] `DATABASE_URL` uses asyncpg driver with SSL: `postgresql+asyncpg://...?ssl=require`
- [ ] Tables will be auto-created via FastAPI lifespan event

---

## Step 6: Post-deploy smoke tests

```bash
BACKEND=https://your-backend-aca-fqdn
FRONTEND=https://your-frontend-aca-fqdn

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
  -F "file=@test.pdf" -F "uploaded_by=test" -w "\n%{http_code}"
# Expected: JSON response + 202 status

# 6. Chat endpoint responds
curl -s -X POST $BACKEND/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Which contracts expire soon?"}' | python3 -m json.tool
# Expected: JSON with answer and sources
```

---

## Step 7: Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Backend 500 on startup | Missing env variable | Check logs for pydantic_settings validation error |
| Upload returns 400 | Invalid file type or size | Check MIME type validation |
| Document stuck in "uploading" | BackgroundTask failed | Check ACA logs for Azure SDK errors |
| OCR returns empty text | Azure DI endpoint/key wrong | Verify credentials in ACA env vars |
| Frontend shows empty dashboard | `NEXT_PUBLIC_API_URL` not set at build time | Rebuild frontend image with correct build arg |
| CORS errors in browser console | Frontend URL not in `CORS_ORIGINS` | Add ACA frontend FQDN to CORS_ORIGINS |
| Database connection refused | Azure PG firewall or SSL issue | Check firewall rules, verify `?ssl=require` in URL |
| Chat returns empty | AI Search index empty or not synced | Run seed script, verify index has documents |
