# backend/app/middleware/logging.py
import logging.config
import json
from datetime import datetime
from fastapi import Request

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "json": {
            "format": "%(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True
        }
    }
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)

class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = datetime.now()

        async def send_with_logging(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = (datetime.now() - start_time).total_seconds()
                
                log_data = {
                    "timestamp": start_time.isoformat(),
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_seconds": duration,
                    "client_ip": request.client.host if request.client else "unknown"
                }
                
                logger = logging.getLogger("http")
                logger.info(json.dumps(log_data))
            
            await send(message)

        await self.app(scope, receive, send_with_logging)
