"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.backfill import router as backfill_router
from app.api.ingest import router as ingest_router
from app.api.router import router
from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables, recover stale docs. Shutdown: nothing special needed."""
    await init_db()

    # Recover stale processing documents (stuck from prior server restart)
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import select, update
    from app.database import AsyncSessionLocal
    from app.models.document import Document

    async with AsyncSessionLocal() as session:
        stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
        processing_statuses = ("uploading", "ocr_complete", "classified")
        result = await session.execute(
            update(Document)
            .where(Document.status.in_(processing_statuses))
            .where(Document.updated_at < stale_cutoff)
            .values(
                status="error",
                error_message="Processing interrupted — please click Reprocess to retry.",
            )
            .returning(Document.id)
        )
        recovered = result.all()
        if recovered:
            await session.commit()
            import logging
            logging.getLogger(__name__).info("Recovered %d stale documents on startup", len(recovered))

    yield


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

# Serve UI static files if the ui/ directory exists (bundled in Docker image)
_ui_dir = os.path.join(os.path.dirname(__file__), "..", "..", "ui")
if os.path.isdir(_ui_dir):
    app.mount("/ui", StaticFiles(directory=_ui_dir, html=True), name="ui")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(_ui_dir, "index.html"))
