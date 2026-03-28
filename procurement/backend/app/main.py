"""FastAPI application entry point."""

import logging
import os
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func

from app.api.backfill import router as backfill_router
from app.api.ingest import router as ingest_router
from app.api.router import router
from app.config import settings
from app.database import init_db, AsyncSessionLocal

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("procurement")

# ── Application Insights (OpenTelemetry) ──────────────────────────────────────
# Only configure when running on Azure App Service (WEBSITE_INSTANCE_ID is set).
# Skipped locally to avoid namespace-package warnings from the WatchFiles subprocess.
_on_azure = bool(os.environ.get("WEBSITE_INSTANCE_ID"))
if _on_azure and settings.applicationinsights_connection_string:
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(
            connection_string=settings.applicationinsights_connection_string,
            # Capture ALL loggers (root logger), not just "procurement"
            logger_name="",
        )
        # Ensure uvicorn loggers propagate to root so OTel picks them up
        for _uvicorn_logger in ("uvicorn", "uvicorn.error", "uvicorn.access"):
            logging.getLogger(_uvicorn_logger).propagate = True
        logger.info("Application Insights configured successfully")
    except Exception as _ai_exc:  # noqa: BLE001
        logger.warning("Failed to configure Application Insights: %s", _ai_exc)


async def _seed_default_rules() -> None:
    """Seed default validation policy rules on first startup (idempotent)."""
    from app.models.document import ValidationRuleConfig, ValidationRuleAuditLog

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(func.count(ValidationRuleConfig.id))
        )
        count = result.scalar_one()
        if count > 0:
            logger.info("Validation rules table already has %d rows — skipping seed", count)
            return

        # ── Define default rules ─────────────────────────────────────────
        default_rules: list[dict] = [
            # 1. High-value contract scrutiny
            {
                "name": "High-value contract scrutiny",
                "description": "Flag contracts exceeding $500,000 for additional review",
                "rule_type": "threshold",
                "scope": "global",
                "department": None,
                "severity": "warning",
                "status": "active",
                "field_name": "total_amount",
                "operator": "gt",
                "threshold_value": "500000",
                "message_template": "Contract value ${value} exceeds $500,000 threshold — requires additional scrutiny",
                "suggestion": "Route to department head for review before approval",
                "policy_statement": None,
                "enabled": True,
                "created_by": "system",
            },
            # 2. Require bond for Public Works
            {
                "name": "Require bond for Public Works",
                "description": "Public Works contracts must specify bond requirements",
                "rule_type": "required_field",
                "scope": "department",
                "department": "PUBLIC_WORKS",
                "severity": "error",
                "status": "active",
                "field_name": "bond_required",
                "operator": "is_not_empty",
                "threshold_value": None,
                "message_template": "Public Works contracts must specify bond requirements",
                "suggestion": "Verify bond requirement and amount with the vendor",
                "policy_statement": None,
                "enabled": True,
                "created_by": "system",
            },
            # 3. Verify Richmond district reference
            {
                "name": "Verify Richmond district reference",
                "description": "Verify referenced locations are within Richmond city limits",
                "rule_type": "district_check",
                "scope": "global",
                "department": None,
                "severity": "warning",
                "status": "active",
                "field_name": None,
                "operator": None,
                "threshold_value": None,
                "message_template": "Document references locations — verify they are within Richmond city limits",
                "suggestion": "Confirm all referenced locations are valid Richmond districts or neighborhoods",
                "policy_statement": None,
                "enabled": True,
                "created_by": "system",
            },
            # 4. Construction environmental compliance
            {
                "name": "Construction environmental compliance",
                "description": "Require environmental liability insurance for construction contracts",
                "rule_type": "semantic_policy",
                "scope": "department",
                "department": "PUBLIC_WORKS",
                "severity": "error",
                "status": "active",
                "field_name": None,
                "operator": None,
                "threshold_value": None,
                "message_template": None,
                "suggestion": "Require the vendor to provide environmental liability insurance documentation",
                "policy_statement": "All construction contracts must include environmental liability insurance coverage and a hazardous materials handling plan if the scope involves demolition, excavation, or renovation of structures built before 1980.",
                "enabled": True,
                "created_by": "system",
            },
            # 5. MBE/WBE participation for large contracts
            {
                "name": "MBE/WBE participation for large contracts",
                "description": "Flag large contracts without MBE/WBE participation plans",
                "rule_type": "semantic_policy",
                "scope": "global",
                "department": None,
                "severity": "warning",
                "status": "active",
                "field_name": None,
                "operator": None,
                "threshold_value": None,
                "message_template": None,
                "suggestion": "Request MBE/WBE participation plan from the vendor",
                "policy_statement": "Contracts over $50,000 should include a Minority Business Enterprise (MBE) or Women's Business Enterprise (WBE) participation plan with a specific percentage commitment. If no MBE/WBE plan is present, flag for review.",
                "enabled": True,
                "created_by": "system",
            },
            # 6. Subcontractor flow-down clauses
            {
                "name": "Subcontractor flow-down clauses",
                "description": "Ensure subcontracting provisions include flow-down clauses",
                "rule_type": "semantic_policy",
                "scope": "global",
                "department": None,
                "severity": "info",
                "status": "active",
                "field_name": None,
                "operator": None,
                "threshold_value": None,
                "message_template": None,
                "suggestion": "Review subcontracting provisions and ensure flow-down clauses are present",
                "policy_statement": "Contracts that authorize subcontracting must include flow-down clauses requiring subcontractors to meet the same insurance, bonding, and compliance requirements as the prime contractor.",
                "enabled": True,
                "created_by": "system",
            },
            # 7. Contract duration reasonableness
            {
                "name": "Contract duration reasonableness",
                "description": "Flag contracts with duration exceeding 5 years",
                "rule_type": "date_window",
                "scope": "global",
                "department": None,
                "severity": "warning",
                "status": "active",
                "field_name": "expiration_date",
                "operator": None,
                "threshold_value": "1825",
                "message_template": "Contract duration exceeds 5 years — verify this is intentional",
                "suggestion": "Confirm extended contract duration is appropriate for the scope of work",
                "policy_statement": None,
                "enabled": True,
                "created_by": "system",
            },
            # 8. Insurance adequacy for high-value contracts
            {
                "name": "Insurance adequacy for high-value contracts",
                "description": "Require minimum insurance coverage for high-value Finance contracts",
                "rule_type": "semantic_policy",
                "scope": "department",
                "department": "FINANCE",
                "severity": "error",
                "status": "active",
                "field_name": None,
                "operator": None,
                "threshold_value": None,
                "message_template": None,
                "suggestion": "Require vendor to provide certificate of insurance meeting minimum coverage requirements",
                "policy_statement": "Contracts over $100,000 must specify general liability insurance of at least $1,000,000 per occurrence and automobile liability of at least $500,000. The City of Richmond must be named as additional insured.",
                "enabled": True,
                "created_by": "system",
            },
            # 9. Prevailing wage compliance (DRAFT)
            {
                "name": "Prevailing wage compliance",
                "description": "Require prevailing wage rates for publicly funded construction contracts",
                "rule_type": "semantic_policy",
                "scope": "global",
                "department": None,
                "severity": "warning",
                "status": "draft",
                "field_name": None,
                "operator": None,
                "threshold_value": None,
                "message_template": None,
                "suggestion": None,
                "policy_statement": "Publicly funded construction contracts must include prevailing wage rate requirements per the Davis-Bacon Act or Virginia prevailing wage law.",
                "enabled": True,
                "created_by": "system",
            },
            # 10. Emergency procurement justification (DRAFT)
            {
                "name": "Emergency procurement justification",
                "description": "Require written justification for emergency procurements",
                "rule_type": "semantic_policy",
                "scope": "global",
                "department": None,
                "severity": "warning",
                "status": "draft",
                "field_name": None,
                "operator": None,
                "threshold_value": None,
                "message_template": None,
                "suggestion": None,
                "policy_statement": "Emergency procurement contracts must include a written justification explaining why competitive bidding was not feasible and the specific emergency circumstances.",
                "enabled": True,
                "created_by": "system",
            },
        ]

        rules: list[ValidationRuleConfig] = []
        for rule_data in default_rules:
            rule = ValidationRuleConfig(**rule_data)
            session.add(rule)
            rules.append(rule)

        # Flush to populate rule IDs before creating audit logs
        await session.flush()

        for rule in rules:
            audit = ValidationRuleAuditLog(
                rule_id=rule.id,
                rule_name=rule.name,
                action="created",
                changed_by="system",
                new_values={"status": rule.status, "enabled": rule.enabled},
            )
            session.add(audit)

        await session.commit()
        logger.info("Seeded %d default validation rules", len(rules))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables, recover stale docs. Shutdown: nothing special needed."""
    logger.info("Procurement API starting up — environment: %s", settings.environment)

    # TODO: re-enable once Azure SQL is configured
    # await init_db()

    # Recover stale processing documents (MSSQL-compatible, no .returning())
    # TODO: re-enable once Azure SQL init_db is configured
    # from datetime import datetime, timedelta, timezone
    # from sqlalchemy import select, update
    # from app.database import AsyncSessionLocal
    # from app.models.document import Document
    # async with AsyncSessionLocal() as session:
    #     stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    #     processing_statuses = ("uploading", "ocr_complete", "classified")
    #     stale_result = await session.execute(
    #         select(Document.id)
    #         .where(Document.status.in_(processing_statuses))
    #         .where(Document.updated_at < stale_cutoff)
    #     )
    #     stale_ids = [row[0] for row in stale_result.all()]
    #     if stale_ids:
    #         await session.execute(
    #             update(Document)
    #             .where(Document.id.in_(stale_ids))
    #             .values(
    #                 status="error",
    #                 error_message="Processing interrupted — please click Reprocess to retry.",
    #             )
    #         )
    #         await session.commit()
    #         logger.info("Recovered %d stale documents on startup", len(stale_ids))

    # Seed default policy rules (idempotent — skips if table already has rows)
    try:
        await _seed_default_rules()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to seed default validation rules: %s", exc)

    logger.info("Procurement API startup complete")
    yield
    logger.info("Procurement API shutting down")


app = FastAPI(
    title="Procurement Document Processing API",
    description=(
        "AI-powered procurement document processing for City of Richmond. "
        "Decision-support tool — AI-assisted, requires human review."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — explicit origins only, never allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(ingest_router)
app.include_router(backfill_router)


@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        if response.status_code >= 500:
            logger.error("HTTP %s %s → %d", request.method, request.url.path, response.status_code)
        return response
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error(
            "Unhandled exception on %s %s:\n%s",
            request.method,
            request.url.path,
            tb,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {type(exc).__name__}: {exc}"},
        )

# Serve UI static files — mounted at "/" so /login.html, /document.html etc. resolve correctly.
# API routers are already registered above and take priority over the static mount.
# Container: WORKDIR=/app, so ui is at /app/ui
# Local:     __file__ = …/procurement/backend/app/main.py → go up 3 levels to repo root
_ui_dir = "/app/ui" if os.path.isdir("/app/ui") else os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "ui")
)
if os.path.isdir(_ui_dir):
    app.mount("/", StaticFiles(directory=_ui_dir, html=True), name="ui")
