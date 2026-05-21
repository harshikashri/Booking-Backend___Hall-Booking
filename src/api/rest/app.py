"""FastAPI application assembly for the booking backend REST service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from src.data.clients.postgres import get_or_create_engine
from src.data.models.postgres.base import Base
from src.api.rest.routes.booking import router as booking_router
from src.api.rest.routes.facility import router as facilities_router
from src.api.rest.routes.favorite import router as favorites_router
from src.api.rest.routes.freeSlots import router as free_slots_router
from src.api.rest.routes.halls import router as halls_router
from src.api.rest.routes.health import router as health_router
from src.api.rest.routes.notifications import router as notifications_router
from src.api.rest.routes.search import router as search_router
from src.api.rest.middleware.cors import add_cors_middleware
from src.api.rest.middleware.error_handler import add_error_handlers




@asynccontextmanager
async def lifespan(app: FastAPI):
	"""Run startup database checks and dispose of the engine on shutdown."""

    engine = get_or_create_engine()

    # Startup validation keeps the app honest about database connectivity.
    try:

        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.run_sync(Base.metadata.create_all)

        print("Database connected")

    except Exception as e:

        print("Database connection failed")
        print(e)

    

    yield

    # Release pooled database connections during shutdown.
    await engine.dispose()

    print("Database connections closed")


app = FastAPI(
    title="Base REST Service Template",
    lifespan=lifespan,
)

add_error_handlers(app)
add_cors_middleware(app)

app.include_router(router=health_router)
app.include_router(router=halls_router)
app.include_router(router=facilities_router)
app.include_router(router=favorites_router)
app.include_router(router=free_slots_router)
app.include_router(router=booking_router)
app.include_router(router=notifications_router)
app.include_router(router=search_router)


