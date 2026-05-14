"""
Author: Sean Froning
Created Date: 5.9.2026
Core AI API orchestration
"""

from fastapi import APIRouter, Depends
from focus_python import (
    dependency,
    error,
    logging,
    queue,
)
from focus_python import (
    PredictionType,
    TRAINING_JOBS,
)
from .schemas import TrainingRequest, TrainingResponse

logger = logging.get_logger(__name__)

router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)


training_available: bool = False
try:
    from .background import TrainingBackgroundJobs
    from .services import TrainingServices

    training_available = True
except ImportError as e:
    training_available = False
    logger.error("Failed to import Training", error=str(e))
except Exception as e:
    training_available = False
    logger.error(f"Failed to boot up Training: {str(e)}")


@router.post(
    "/train/controllable_prd", dependencies=[Depends(dependency.get_token_header)]
)
async def model_train(_request: TrainingRequest) -> TrainingResponse:
    """Train batch of sklearn models for controllable prd"""
    if not training_available:
        raise error("Training service unavailable", status_code=503)

    prediction_type = PredictionType.CONTROLLABLE_PRD

    try:
        batch_id = TrainingServices.create_batch(prediction_type)
    except Exception as e:
        logger.error("training_batch_seed_failed", error=str(e))
        raise error("Model training failed to start", status_code=500)

    try:
        specs = []
        for training_type in TRAINING_JOBS.values():
            specs.append(
                {
                    "func": TrainingBackgroundJobs.background_model_train,
                    "args": (training_type.value, batch_id, prediction_type.value),
                    "job_id": f"model_training_{training_type.value}_{batch_id}",
                    "job_timeout": 6000,
                }
            )
        jobs = queue.enqueue_jobs(specs)
        return TrainingResponse(job_ids=[job.id for job in jobs])
    except Exception as e:
        logger.error("model_training_enqueue_failed", batch=batch_id, error=str(e))
        raise error("Model training failed", status_code=500)
