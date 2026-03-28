"""FastAPI application entry point."""

import logging
import os
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.backfill import router as backfill_router
from app.api.ingest import router as ingest_router
from app.api.router import router
from app.config import settings
from app.database import init_db

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("procurement")

# ── Application Insights (OpenTelemetry) ──────────────────────────────────────
# Must be called before the FastAPI app is created so all traces are captured.
if settings.applicationinsights_connection_string:
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
