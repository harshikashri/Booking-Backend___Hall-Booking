
from typing import AsyncGenerator

from src.data.clients.postgres import get_session_factory

from sqlalchemy.ext.asyncio import AsyncSession

# =========================
# Database Dependency
# =========================

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:

    session_factory = get_session_factory()

    async with session_factory() as session:

        try:

            yield session

            await session.commit()

        except Exception:

            await session.rollback()
            raise
