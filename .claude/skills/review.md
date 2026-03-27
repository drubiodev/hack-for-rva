---
description: Context-aware code review — auto-runs git diff, detects backend/frontend/full-stack scope, applies relevant guardrails and quality checks
---

Perform a thorough code review of recent changes in the HackathonRVA 311 SMS project.

---

## Step 1: Gather changes

Run `git diff HEAD` to see all uncommitted changes. If the working tree is clean, run `git diff HEAD~1` to review the most recent commit and note that you are reviewing a committed change.

Identify which layers changed:
- Files under `backend/` → apply **Backend review**
- Files under `frontend/` → apply **Frontend review**
- `docs/openapi.yaml` or both `backend/` and `frontend/` → apply **API contract review**
- Root config, Dockerfile, Railway config → apply **Deployment review**

---

## Step 2: Guardrail scan — run on all changes before anything else

These are hard architecture violations. Flag each one as `🚨 BLOCK` and do not continue to style review until addressed.

| Pattern | File scope | Violation |
|---|---|---|
| `import langgraph` / `from langgraph` | `backend/` | Plan mandates plain Python state machine |
| `from celery` / `import celery` | `backend/` | Plan mandates FastAPI BackgroundTasks |
| `import redis` / `Redis(` | `backend/` | Plan mandates in-memory dict or PostgreSQL |
| `new WebSocket(` / `EventSource(` | `frontend/` | Plan mandates TanStack Query 30s polling |
| Hardcoded API key, token, or 32+ char secret string | Anywhere | Secrets must be in environment variables |
| `import.*react-leaflet` at top-level outside `LeafletMap.tsx` | `frontend/` | SSR crash in Next.js — must use dynamic import |
| `output: "standalone"` removed from `next.config.ts` | `frontend/` | Railway Docker build will be 2GB+ |
| Non-200 HTTP response returned from `/webhooks/sms` error path | `backend/` | Twilio retries on 4xx/5xx — causes duplicate reports |
| Sync `Session` from SQLAlchemy in async endpoint | `backend/` | Deadlocks under concurrent load |
| Inline `fetch()` call inside a React component | `frontend/` | Must use `src/lib/api.ts` functions only |

---

## Step 3: Backend review (apply if `backend/` files changed)

### Async correctness
- All database operations use `await` with `AsyncSession` — no blocking calls in async functions
- No `time.sleep()` or sync file I/O in request handlers
- `BackgroundTasks.add_task()` used for writes that don't need to complete before the SMS reply

### Twilio handling
- Signature validation (`RequestValidator.validate()`) on every webhook request
- URL reconstruction handles Railway's `X-Forwarded-Proto` header for correct HTTPS URL
- All exception paths catch broadly and return valid TwiML — never propagate to 500
- Phone numbers in logs are redacted (`phone[-4:]`) — no full numbers in log output

### AI / LangChain patterns
- `with_structured_output(PydanticModel)` used — no manual JSON parsing
- System prompts in `ai/prompts.py` — no inline prompt strings in `router.py` or `service.py`
- Classifier deployment: `gpt-41-nano` | Responder deployment: `gpt-4o-mini`
- SMS body wrapped in delimiters in prompt to limit prompt injection blast radius

### API design
- All response shapes match `docs/openapi.yaml` field names exactly
- Pydantic response models on every endpoint — no bare `dict` returns
- Query parameters use `Query()` with types and descriptions
- Pagination (`limit`, `offset`) on list endpoints

### Security
- No SQL string formatting — SQLAlchemy ORM or parameterized `text()`
- No secrets in source code
- CORS `allow_origins` uses `settings.frontend_url`, not `"*"`

---

## Step 4: Frontend review (apply if `frontend/` files changed)

### Data fetching
- All fetch calls in `src/lib/api.ts` — none inline in components
- `useQuery` with `refetchInterval: 30_000` for all live dashboard data
- `useMutation` + `queryClient.invalidateQueries()` after status updates
- TypeScript types in `src/lib/types.ts` — field names match `docs/openapi.yaml`

### Map / Leaflet
- `react-leaflet` only imported inside `src/components/LeafletMap.tsx`
- Map page uses `dynamic(() => import("@/components/LeafletMap"), { ssr: false })`
- No Leaflet imports at the page or layout level

### Next.js App Router
- `output: "standalone"` present in `next.config.ts`
- `"use client"` used only on interactive leaf components, not on page-level layouts
- Server Components used where possible (data fetching pages without interactivity)
- No `window` or `document` access outside `"use client"` components

### shadcn/ui
- `src/components/ui/` files not hand-edited
- shadcn components used for all standard UI elements

### Environment
- No hardcoded backend URL strings — always `process.env.NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_` prefix on any env var that needs to be accessible in the browser

---

## Step 5: API contract review (apply if `docs/openapi.yaml` changed or both backend and frontend changed)

- All modified FastAPI endpoint signatures are reflected in `docs/openapi.yaml`
- `src/lib/types.ts` field names match the OpenAPI spec exactly — check every field
- No breaking changes (renamed fields, type changes, removed fields) without explicit callout
- New enum values added to both the OpenAPI spec and the TypeScript union types
- `ServiceRequest`, `ServiceRequestList`, `AnalyticsSummary` schemas unchanged unless intentional

---

## Step 6: Deployment review (apply if Dockerfile, Railway config, or root config changed)

- `backend/Dockerfile` sets `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]`
- `frontend/Dockerfile` uses the `standalone` output directory
- `.env` is in `.gitignore` — `.env.example` exists with placeholder values

---

## Output format

```
## Guardrail Scan
✅ No violations  OR  🚨 [N] blocking violations:
  - BLOCK: [pattern] in [file:line] — [rule]

## [Backend / Frontend / API Contract / Deployment] Review

### Critical (must fix before demo)
- ...

### Warnings (should fix)
- ...

### Suggestions (nice to have)
- ...

## Overall
[2–3 sentence assessment. Be direct — if it's solid, say so.]
```

Do not invent issues to sound thorough. If a section has nothing to flag, say "No issues found."
