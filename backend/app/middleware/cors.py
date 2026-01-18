from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

def setup_cors(app):
    """Production CORS setup"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React dev
            "https://your-domain.com",
            "*"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
