"""
Author: Sean Froning
Created Date: 5.3.2026
Lifespan events for FastAPI app
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI  # pyright: ignore[reportMissingImports]
from focus_python import db_pool, logging, queue  # pyright: ignore[reportMissingImports]
from ml import model_registry  # pyright: ignore[reportMissingImports]

logger = logging.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    db_pool._ensure_pool()
    queue.get_connection()
    try:
        model_registry.load()
    except Exception as e:
        logger.warning("registry_warm_failed", error=str(e))
    app.state.db_pool = db_pool
    app.state.queue = queue
    app.state.model_registry = model_registry

    yield

    logger.info("Application shutdown")
    queue.close()
    db_pool.close()
