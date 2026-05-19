from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy import text
from src.data.clients.postgres import get_or_create_engine

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

@router.get(
    "/",
    status_code=status.HTTP_200_OK
)
async def health_check():
    engine = get_or_create_engine()

    # Startup
    try:

        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        print("Database connected")
        return {"status": "okay"}

    except Exception as e:

        print("Database connection failed")
        print(e)