# backend/app/middleware/error_handler.py
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)

async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions"""
    logger.error(f"App exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.exception(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
