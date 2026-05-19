from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from src.data.clients.postgres import get_or_create_engine
from src.api.rest.routes.facility import router as facilities_router
from src.api.rest.routes.halls import router as halls_router
from src.api.rest.routes.health import router as health_router




@asynccontextmanager
async def lifespan(app: FastAPI):

    engine = get_or_create_engine()

    # Startup
    try:

        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        print("Database connected")

    except Exception as e:

        print("Database connection failed")
        print(e)

    

    yield

    # Shutdown
    await engine.dispose()

    print("Database connections closed")


app = FastAPI(
    title="Base REST Service Template",
    lifespan=lifespan,
)

app.include_router(router=health_router)
app.include_router(router=halls_router)
app.include_router(router=facilities_router)


