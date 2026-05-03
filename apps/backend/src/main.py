"""
Author: Sean Froning
Created Date: 5.3.2026
Main entrypoint for Focus backend API
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI  # pyright: ignore[reportMissingImports]
from focus_python import config, exception, logging, middleware  # pyright: ignore[reportMissingImports]
from core import health, lifespan

# Setup structured logging
logging.setup_structured_logging()
logger = logging.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Focus backend API",
    lifespan=lifespan,
    description="Backend API for Focus full stack app",
    version="0.0.1"
)

# Register middleware
app.add_middleware(middleware)

# Register exception handlers
exception.register_exception_handlers(app)

# Include routers
app.include_router(health.router)

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with basic API information and configuration status"""

    return {
        "service": "Focus backend API",
        "version": "0.0.1",
        "status": "running",
        "configuration": {
            "required_services": config.get_required_services_status(),
        },
        "endpoints": {
            "health": "/health",
            "ready": "/ready"
        }
    }
