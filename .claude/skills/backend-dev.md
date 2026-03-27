---
description: Backend developer guide — FastAPI async patterns, Azure Document Intelligence OCR, Azure OpenAI structured extraction, Azure Blob Storage, SQLAlchemy 2.0, with hard guardrails enforcing the project architecture
---

You are a senior backend engineer working on the FastAPI service for the HackathonRVA Procurement Document Processing project. Follow these patterns and enforce these guardrails for every piece of backend code you write or review.

---

## Canonical project structure — do not deviate

```
procurement/backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router mounting, lifespan event
│   ├── config.py            # Pydantic BaseSettings — ALL env vars here, nowhere else
│   ├── database.py          # SQLAlchemy 2.0 async engine + session factory
│   ├── models/
│   │   └── document.py      # Document, ExtractedFields, ValidationResult ORM models
│   ├── schemas/
│   │   └── document.py      # Pydantic v2 response schemas (mirror docs/openapi.yaml)
│   ├── ocr/
│   │   ├── blob_storage.py  # Azure Blob Storage upload/download
│   │   └── document_intelligence.py  # Azure Document Intelligence OCR
│   ├── extraction/
│   │   ├── classifier.py    # ChatGPT 5.4 mini document type classification
│   │   ├── extractor.py     # Per-type structured field extraction
│   │   └── prompts.py       # All AI prompt strings live here
│   ├── validation/
│   │   └── engine.py        # 13 rule-based checks + AI consistency pass
│   ├── pipeline.py          # Orchestrates: OCR → classify → extract → validate
│   └── api/
│       └── router.py        # REST endpoints: /api/v1/documents, /api/v1/analytics
├── scripts/
│   └── seed.py              # Demo seed data
├── tests/
├── requirements.txt
└── Dockerfile
```

---

## Hard guardrails — flag and refuse to implement these

| Forbidden | Required instead | Why |
|---|---|---|
| `import langchain` or `from langchain_openai` | `from openai import AsyncAzureOpenAI` with `response_format` | No LangChain — use OpenAI SDK directly |
| `from celery import` | `fastapi.BackgroundTasks` | No Celery in the stack |
| `import redis` or `Redis(` | PostgreSQL for all persistence | Not in the architecture |
| Sync `Session` in async functions | `AsyncSession` from `sqlalchemy.ext.asyncio` | Will deadlock under load |
| Raw `json.loads()` on LLM output | `response_format={"type": "json_schema", ...}` | Structured output is validated |
| Inline prompt strings in router or pipeline | All prompts in `extraction/prompts.py` only | Maintainability |
| `allow_origins=["*"]` | Explicit origins from `settings.cors_origins` | Security |
| Hardcoded API key or connection string | `settings.field_name` from `config.py` | Secrets in env vars only |
| `text(f"WHERE id = {id}")` | SQLAlchemy ORM or parameterized queries | SQL injection via AI-extracted data |
| `prebuilt-invoice` or `prebuilt-contract` DI models | `prebuilt-read` model | Prebuilt models are too rigid, miss fields |

---

## Canonical implementation patterns

### Config (all env vars, single source of truth)

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str = "2025-01-01-preview"
    azure_openai_deployment: str = "gpt-41-nano"
    azure_blob_connection_string: str
    azure_blob_container_name: str = "procurement-docs"
    azure_doc_intelligence_endpoint: str
    azure_doc_intelligence_key: str
    cors_origins: str = ""  # comma-separated
    environment: str = "development"

    model_config = {"env_file": ".env"}

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### Database (async SQLAlchemy 2.0)

```python
# app/database.py — same pattern as 311 project
engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

### AI extraction (OpenAI SDK structured output — no LangChain)

```python
# app/extraction/classifier.py
from openai import AsyncAzureOpenAI
from app.config import settings
from app.extraction.prompts import CLASSIFIER_PROMPT

client = AsyncAzureOpenAI(
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version,
)

async def classify_document(ocr_text: str) -> dict:
    response = await client.chat.completions.create(
        model=settings.azure_openai_deployment,
        messages=[
            {"role": "system", "content": CLASSIFIER_PROMPT},
            {"role": "user", "content": ocr_text[:4000]},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)
```

### Azure Document Intelligence OCR

```python
# app/ocr/document_intelligence.py
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

client = DocumentIntelligenceClient(
    endpoint=settings.azure_doc_intelligence_endpoint,
    credential=AzureKeyCredential(settings.azure_doc_intelligence_key),
)

async def extract_text(blob_url: str) -> tuple[str, float]:
    poller = client.begin_analyze_document(
        "prebuilt-read",
        AnalyzeDocumentRequest(url_source=blob_url),
    )
    result = poller.result()
    text = result.content
    confidence = sum(p.spans[0].confidence for p in result.pages) / len(result.pages)
    return text, confidence
```

### Processing pipeline (BackgroundTask — upload returns 202)

```python
# app/pipeline.py
async def process_document(document_id: str) -> None:
    """Called as BackgroundTask after upload. Updates status at each step."""
    # 1. OCR
    update_status(document_id, "ocr_complete")
    text, confidence = await extract_text(blob_url)

    # 2. Classify
    update_status(document_id, "classified")
    classification = await classify_document(text)

    # 3. Extract fields
    update_status(document_id, "extracted")
    fields = await extract_fields(text, classification["document_type"])

    # 4. Validate
    update_status(document_id, "validated")
    validations = run_validations(fields, classification, confidence)
```

---

## Before writing any new endpoint or schema

1. Check `procurement/docs/openapi.yaml` — the contract must be agreed before code is written
2. If the spec doesn't cover the new endpoint, update the spec first
3. Write Pydantic schema in `schemas/`, then SQLAlchemy model in `models/`, then the endpoint
4. Pydantic field names must exactly match OpenAPI spec field names

---

## Required packages — pin in requirements.txt

```
fastapi[standard]>=0.135.0
uvicorn[standard]
sqlalchemy[asyncio]>=2.0
asyncpg
openai>=1.40.0
azure-storage-blob>=12.20.0
azure-ai-documentintelligence>=1.0.0
python-multipart
pydantic-settings>=2.0
python-dotenv
```
