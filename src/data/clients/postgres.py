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


# Create or Get Existing Engine
def get_or_create_engine() -> AsyncEngine:

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


# Session Factory
def get_session_factory() -> async_sessionmaker[AsyncSession]:

    return async_sessionmaker(
        bind=get_or_create_engine(),

        class_=AsyncSession,

        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


# async def init_db():
#     engine = get_or_create_engine()

#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)