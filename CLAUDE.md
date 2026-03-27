# 311 SMS Civic Service — Agent & Team Context

> Every teammate reads this file on spawn. Keep it concise and authoritative.

## Project Overview

SMS-based 311 reporting system for HackathonRVA 2026. Citizens text reports to a Twilio number, AI classifies them, and city staff see a live dashboard. 48-hour hackathon, ~$65 budget.

## Architecture (non-negotiable)

```
Citizen SMS --> Twilio --> FastAPI backend (AI classify + confirm) --> Supabase PostgreSQL
                                                                          |
                                          Next.js 16 Dashboard <-- REST API (30s polling)
```

| Layer | Tech | Directory |
|---|---|---|
| Backend API | FastAPI, SQLAlchemy 2.0 async, Azure OpenAI, Twilio | `backend/` |
| Frontend | Next.js 16, shadcn/ui, TanStack Query, React-Leaflet | `frontend/` |
| Database | Supabase PostgreSQL (free tier) | external |
| Deployment | Railway (both services) | external |
| API Contract | OpenAPI 3.1.0 | `docs/openapi.yaml` |

## Hard Guardrails

These are deliberate architecture decisions. Do NOT violate without explicit user approval:

- **No LangGraph** — 80-line Python state machine covers the demo
- **No Celery / No Redis** — `FastAPI BackgroundTasks` for async; in-memory dict for session state
- **GPT-4.1-nano for classification** — $0.10/1M tokens, essentially free at demo scale
- **GPT-4o-mini for response generation** — friendly SMS replies
- **`docs/openapi.yaml` is the single source of truth** for frontend/backend interaction
- **No full phone numbers in API responses** — mask as `+1804555****`

## Key Directories

```
backend/app/
  ai/          # classifier (GPT-4.1-nano), responder (GPT-4o-mini), prompts
  sms/         # Twilio webhook handler, conversation state machine
  api/         # REST endpoints: /api/v1/requests, /api/v1/analytics
  models/      # SQLAlchemy 2.0 async models
  schemas/     # Pydantic request/response schemas
  config.py    # Pydantic BaseSettings (env vars)
  database.py  # Async engine + session factory
  main.py      # FastAPI app entry point

frontend/src/  # Next.js 16 App Router

docs/
  openapi.yaml                    # API contract
  product-requirements.md         # OKRs, user stories, demo script
  technical-implementation-plan.md # Task breakdown, ADRs, DB schema
  agent-teams-reference.md        # Agent teams usage guide
```

## Skills Available

Teammates can reference these in `.claude/skills/`:

| Skill | Use for |
|---|---|
| `product-manager` | OKRs, feature prioritization, demo narrative |
| `architect` | Architecture enforcement, OpenAPI maintenance |
| `backend-dev` | FastAPI, Azure OpenAI, Twilio, SQLAlchemy patterns |
| `frontend-dev` | Next.js 16, shadcn/ui, TanStack Query, React-Leaflet |
| `review` | Context-aware code review with guardrail checks |
| `security-audit` | Twilio signatures, CORS, secrets, injection vectors |
| `e2e-test` | Playwright e2e tests against deployed Railway URL |
| `deploy-check` | Railway pre-deployment checklist and smoke tests |
| `debug-sms` | SMS pipeline debugging (webhook -> state machine -> AI -> DB) |
| `commit` | Conventional commits with guardrail scanning |
| `setup-github-action` | Claude Code GitHub Action setup, secrets, troubleshooting |
| `build-with-agent-team` | Orchestrate multi-agent builds with tmux split panes, contracts, and validation |

## Frontend Warning

Next.js 16 has breaking changes from prior versions. Always read the relevant guide in `frontend/node_modules/next/dist/docs/` before writing frontend code. Do not rely on training data for Next.js APIs.

## Team

- **Priyesh** — Backend (FastAPI, AI, SMS pipeline)
- **Daniel** — Frontend (Next.js dashboard)

## Agent Team Conventions

- Each teammate should own **separate files** — never have two teammates editing the same file
- Use `docs/openapi.yaml` as the coordination contract between backend and frontend teammates
- Backend teammates: run `cd backend && python -m pytest` to verify changes
- Frontend teammates: run `cd frontend && npx tsc --noEmit` to type-check
- Aim for **5-6 tasks per teammate** with clear deliverables
- Always shut down teammates before cleaning up the team

## Phase Completion Checklist

At the end of every implementation phase, the lead (or a designated teammate) MUST:

1. **OpenAPI sync check** — verify `docs/openapi.yaml` matches all implemented endpoints. Run: compare response shapes from the live API against the spec. Fix any drift.
2. **Backend tests pass** — run `cd backend && .venv/bin/python -m pytest -v`
3. **Frontend type-check** — run `cd frontend && npx tsc --noEmit`
4. **Git commit** — commit all changes with a conventional commit message before starting the next phase
