"""Database engine and session management."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from backend.config import settings
from backend.db.models import Base


def create_engine() -> AsyncEngine:
    """Create the async SQLAlchemy engine."""

    return create_async_engine(settings.database_url, echo=False)


engine: AsyncEngine = create_engine()
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session."""

    async with SessionLocal() as session:
        yield session


async def create_all() -> None:
    """Create all database tables."""

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
