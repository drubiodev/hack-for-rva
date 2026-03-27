"""SQLAlchemy 2.0 async engine, session factory, and Base model."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Azure PostgreSQL requires SSL; detect by checking for azure in the URL
_connect_args: dict = {}
if "azure" in settings.database_url or "postgres.database.azure.com" in settings.database_url:
    _connect_args["ssl"] = "require"

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """Create all tables on startup (dev convenience; use Alembic in prod)."""
    from app.models.document import (  # noqa: F401 — ensure models are registered
        ActivityLog,
        Document,
        ExtractedFields,
        ValidationResult,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async DB session."""
    async with AsyncSessionLocal() as session:
        yield session
