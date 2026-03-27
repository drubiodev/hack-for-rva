---
description: Generate a conventional commit message for staged changes, scanning for architecture guardrail violations before committing
---

Inspect staged changes and generate a conventional commit message for the HackathonRVA Procurement Document Processing project.

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
| `docs` | Documentation, OpenAPI spec updates |
| `refactor` | Restructuring without behavior change |
| `test` | Tests (pytest, Playwright) |
| `chore` | Azure Container Apps config, Dockerfile, deps, `.env.example` |
| `perf` | Performance improvement |
| `security` | Security fix (file validation, CORS, secrets) |

### Scopes — use these exact names

| Scope | Maps to |
|---|---|
| `ocr` | Azure Document Intelligence, blob storage (`procurement/backend/app/ocr/`) |
| `extraction` | Document classifier, field extractor, prompts (`procurement/backend/app/extraction/`) |
| `validation` | Validation engine, rules (`procurement/backend/app/validation/`) |
| `pipeline` | Processing pipeline orchestrator (`procurement/backend/app/pipeline.py`) |
| `api` | FastAPI REST endpoints (`procurement/backend/app/api/`) |
| `db` | SQLAlchemy models, schema (`procurement/backend/app/models/`) |
| `upload` | Upload page, file drop zone (`procurement/frontend/src/app/dashboard/upload/`) |
| `dashboard` | Next.js pages, layouts (`procurement/frontend/src/app/dashboard/`) |
| `analytics` | Charts, metrics, risk views |
| `deploy` | Azure Container Apps config, Dockerfile |
| `config` | Environment variables, Pydantic settings |
| `openapi` | `procurement/docs/openapi.yaml` contract changes |

### Rules

- Subject: imperative mood, 72 chars max, no trailing period
- Breaking change: add `!` after scope — `feat(api)!: rename document status field`
- If multiple logical changes exist, suggest splitting into separate commits

---

## Guardrail violations — scan before every commit

| Pattern to detect | Rule |
|---|---|
| `import langchain` or `from langchain` | Plan mandates OpenAI SDK directly — no LangChain |
| `from celery` or `import celery` | Plan mandates `FastAPI BackgroundTasks` — no Celery |
| `import redis` or `Redis(` | Plan mandates PostgreSQL — no Redis |
| `new WebSocket(` or `EventSource(` in frontend | Plan mandates TanStack Query polling |
| String literal matching `sk-`, `Bearer `, hardcoded 32+ char hex/base64 | Secrets in env vars only |
| `os.system(` or `subprocess.` inside request handler | Potential command injection |
| `Base.metadata.drop_all` | Destructive migration — confirm intentional |
| Missing `output: "standalone"` in `next.config.ts` | Container builds will balloon to 2GB+ |
| `prebuilt-invoice` or `prebuilt-contract` | Must use `prebuilt-read` model |

---

Generate the commit message now.
