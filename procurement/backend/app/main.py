"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ingest import router as ingest_router
from app.api.router import router
from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables. Shutdown: nothing special needed."""
    await init_db()
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
