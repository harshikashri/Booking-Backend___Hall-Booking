"""Async PostgreSQL engine and session factory helpers."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from src.data.models.postgres.base import Base


from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import settings


DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)


_engine: AsyncEngine | None = None


def get_or_create_engine() -> AsyncEngine:
    """Create the shared async engine once and reuse it across requests."""

    global _engine

    if _engine is None:

        _engine = create_async_engine(
            DATABASE_URL,

            # Connection Pool Settings
            pool_size=10,
            max_overflow=10,
            pool_timeout=10,
            pool_recycle=3600,
            pool_pre_ping=True,

            # AsyncPG Settings
            connect_args={
                "timeout": 180,
                "command_timeout": 2400,
                "server_settings": {
                    "statement_timeout": "2400000",
                },
            },

            echo=True,
        )

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Build the async session factory bound to the shared engine."""

    return async_sessionmaker(
        bind=get_or_create_engine(),

        class_=AsyncSession,

        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )



# The commented init helper is left here intentionally as a local bootstrap aid.