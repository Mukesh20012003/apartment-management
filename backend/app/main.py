# backend/app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.config import settings
from app.events.event_bus import init_event_publisher
from app.api.v1 import users, residents, tickets, visitors, notices, payments
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
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
    lifespan=lifespan
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
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(residents.router, prefix="/api/v1/residents", tags=["Residents"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["Tickets"])
app.include_router(visitors.router, prefix="/api/v1/visitors", tags=["Visitors"])
app.include_router(notices.router, prefix="/api/v1/notices", tags=["Notices"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
