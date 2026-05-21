"""
Author: Sean Froning
Modified Date: 5.21.2026
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
except ImportError as err:
    models_available = False
    logger.error(f"Failed to import Models: {str(err)}")
except Exception as err:
    models_available = False
    logger.error(f"Failed to boot up Models: {str(err)}")


@router.post("/ml/reload", dependencies=[Depends(dependency.get_token_header)])
async def reload_registry(request: ModelRequest) -> ModelResponse:
    """Reload model registry with latest batch winner"""
    if not models_available:
        raise error("Model registry unavailable", status_code=503)

    try:
        await run_in_threadpool(model_registry.load, request.multi_enabled)

        return ModelResponse(model_ids=model_registry.loaded_model_types())
    except RuntimeError as err:
        logger.error("model_registry_unavailable", error=str(err))
        raise error(str(err), status_code=503)
    except Exception as err:
        logger.error("model_registry_failed", error=str(err))
        raise error("Model registry failed", status_code=500)
