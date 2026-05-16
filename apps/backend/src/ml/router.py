"""
Author: Sean Froning
Created Date: 5.16.2026
Core backend API orchestration
"""

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from focus_python import (
    dependency,
    error,
    logging,
)
from .schemas import ModelRequest, ModelResponse

logger = logging.get_logger(__name__)

router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)


models_available: bool = False
try:
    from .registry import registry as model_registry

    models_available = True
except ImportError as e:
    models_available = False
    logger.error(f"Failed to import Models: {str(e)}")
except Exception as e:
    models_available = False
    logger.error(f"Failed to boot up Models: {str(e)}")


@router.post("/ml/reload", dependencies=[Depends(dependency.get_token_header)])
async def reload_registry(_request: ModelRequest) -> ModelResponse:
    """Reload model registry with latest batch winner"""
    if not models_available:
        raise error("Model registry unavailable", status_code=503)

    try:
        await run_in_threadpool(model_registry.load)

        return ModelResponse(model_ids=model_registry.loaded_model_types())
    except RuntimeError as e:
        logger.error("model_registry_unavailable", error=str(e))
        raise error(str(e), status_code=503)
    except Exception as e:
        logger.error("model_registry_failed", error=str(e))
        raise error("Model registry failed", status_code=500)
