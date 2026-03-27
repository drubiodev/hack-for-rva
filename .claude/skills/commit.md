---
description: Generate a conventional commit message for staged changes, scanning for architecture guardrail violations before committing
---

Inspect staged changes and generate a conventional commit message for the HackathonRVA 311 SMS project.

## Steps

1. Run `git diff --staged` to see all staged changes
2. If nothing is staged, run `git status` and note what is unstaged, then ask whether to stage specific files
3. Scan every changed file for guardrail violations (see below) — report any found **before** generating the message
4. Generate the commit message

---

## Conventional commit format

```
<type>(<scope>): <subject>

[optional body — explain WHY, not WHAT]
```

### Types

| Type | When to use |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation, OpenAPI spec updates, `docs/openapi.yaml` |
| `refactor` | Restructuring without behavior change |
| `test` | Playwright e2e tests only |
| `chore` | Railway config, Dockerfile, deps, `.env.example` |
| `perf` | Performance improvement |
| `security` | Security fix (Twilio validation, CORS, secrets) |

### Scopes — use these exact names

| Scope | Maps to |
|---|---|
| `sms` | Twilio webhook, conversation state machine (`backend/app/sms/`) |
| `ai` | Azure OpenAI classifier, LangChain, prompts (`backend/app/ai/`) |
| `api` | FastAPI REST endpoints (`backend/app/api/`) |
| `db` | SQLAlchemy models, schema, Alembic (`backend/app/models/`, `backend/app/database.py`) |
| `dashboard` | Next.js pages, layouts (`frontend/src/app/dashboard/`) |
| `map` | React-Leaflet map view |
| `analytics` | Charts, metrics, KPI views |
| `deploy` | Railway config, Dockerfile |
| `config` | Environment variables, Pydantic settings |
| `openapi` | `docs/openapi.yaml` contract changes |

### Rules

- Subject: imperative mood, ≤72 chars, no trailing period
- Breaking change: add `!` after scope — `feat(api)!: rename request status field`
- If multiple logical changes exist, suggest splitting into separate commits and list suggested messages for each

---

## Guardrail violations — scan for these before every commit

For each violation found, print a `⚠️ GUARDRAIL:` block with the file path, line number, and the rule being broken. Ask whether to proceed.

| Pattern to detect | Rule |
|---|---|
| `import langgraph` or `from langgraph` | Plan mandates plain Python state machine — LangGraph is out of scope |
| `from celery` or `import celery` | Plan mandates `FastAPI BackgroundTasks` — no Celery |
| `import redis` or `Redis(` anywhere in backend | Plan mandates in-memory dict or PostgreSQL — no Redis |
| `new WebSocket(` or `EventSource(` in `frontend/` | Plan mandates TanStack Query `refetchInterval: 30_000` — no WebSockets or SSE |
| String literal matching `sk-`, `Bearer `, hardcoded 32+ char hex/base64 | Secrets must live in environment variables only |
| `os.system(` or `subprocess.` inside any request handler | Potential command injection — flag for review |
| `Base.metadata.drop_all` | Destructive migration — confirm intentional |
| Direct `import.*react-leaflet` outside `LeafletMap.tsx` | SSR crash risk — must use `dynamic()` import |
| Missing `output: "standalone"` removed from `next.config.ts` | Railway builds will balloon to 2GB+ |

---

Generate the commit message now.
