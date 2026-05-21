from typing import AsyncGenerator

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from jose import JWTError
from jose import jwt

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.data.clients.postgres import get_session_factory
from src.core.services.notification_service import publish_pending_notifications

# =========================
# Database Dependency
# =========================

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:

    session_factory = get_session_factory()

    async with session_factory() as session:

        try:

            yield session

            await session.commit()
            await publish_pending_notifications(session)

        except Exception:

            await session.rollback()
            raise


security = HTTPBearer()


def _decode_token(credentials: HTTPAuthorizationCredentials):

    try:
        return jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):

    payload = _decode_token(credentials)

    if not payload.get("username"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return payload


def get_current_user_from_token(token: str):
    payload = _decode_token_value(token)

    if not payload.get("username"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return payload


def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):

    payload = _decode_token(credentials)

    role = payload.get("role")
    username = payload.get("username")

    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return payload


def _decode_token_value(token: str):
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
