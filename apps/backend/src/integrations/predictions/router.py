"""
Author: Sean Froning
Created Date: 5.9.2026
Core backend API orchestration
"""
from fastapi import APIRouter, Depends  # pyright: ignore[reportMissingImports]
from focus_python import dependency, error, logging  # pyright: ignore[reportMissingImports]
from focus_python import PredictionType  # pyright: ignore[reportMissingImports]
from .schemas import PredictionRequest, PredictionResponse

logger = logging.get_logger(__name__)

router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)


predictions_available: bool = False
try:
    from .services import InferenceServices
    predictions_available = True
except Exception as e:
    predictions_available = False
    logger.error(f"Failed to import Predictions: {str(e)}")


@router.post("/predict/controllable_prd", dependencies=[Depends(dependency.get_token_header)])
async def model_predict(request: PredictionRequest) -> PredictionResponse:
    """Retrieve controllable PRD prediction(s) from the latest training batch"""
    if not predictions_available:
        raise error("Predictions service unavailable", status_code=503)

    logging.bind_job_context(property_id=request.property_id)
    try:
        predictions = InferenceServices.predict(
            property_id=request.property_id,
            multi_enabled=request.multi_enabled,
            prediction_type=PredictionType.CONTROLLABLE_PRD,
        )
        return PredictionResponse(predictions=predictions)
    except ValueError as e:
        logger.warning("model_prediction_rejected", error=str(e))
        raise error(str(e), status_code=404)
    except RuntimeError as e:
        logger.error("model_prediction_unavailable", error=str(e))
        raise error(str(e), status_code=503)
    except Exception as e:
        logger.error("model_prediction_failed", error=str(e))
        raise error("Model prediction failed", status_code=500)
    finally:
        logging.unbind_job_context()
