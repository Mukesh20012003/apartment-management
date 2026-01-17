# backend/app/main.py
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.events.event_bus import init_event_publisher
from app.api.v1 import users, tickets, residents, flats, visitors, notices, payments, health  # include only modules that actually exist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting up application...")
    try:
        await init_event_publisher()
    except Exception as e:
        logger.error(f"Failed to initialize event publisher: {e}")

    yield

    # Shutdown
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}

# Include routers
app.include_router(users.router)
app.include_router(tickets.router)
app.include_router(residents.router)
app.include_router(flats.router)
app.include_router(visitors.router)
app.include_router(notices.router)
app.include_router(payments.router)
app.include_router(health.router)

# Add residents/visitors/notices/payments when those modules exist:
# from app.api.v1 import residents, visitors, notices, payments



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
