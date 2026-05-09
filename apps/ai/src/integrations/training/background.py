"""
Author: Sean Froning
Created Date: 5.9.2026
Background functions for model training
"""
from focus_python import logging  # pyright: ignore[reportMissingImports]
from focus_python import PredictionType, TrainingType  # pyright: ignore[reportMissingImports]
from .services import TrainingServices

logger = logging.get_logger(__name__)


class TrainingBackgroundJobs:
    """Operations for background jobs from Training"""

    @staticmethod
    def background_model_train(
        training_type: str,
        batch_id: str,
        prediction_type: str = PredictionType.CONTROLLABLE_PRD.value,
    ) -> None:
        """Background: Train single sklearn model by type/batch/prediction"""
        type_enum = TrainingType(training_type)
        prediction_enum = PredictionType(prediction_type)
        logging.bind_job_context(training_id=f"{type_enum.value}:{batch_id}")
        try:
            TrainingServices.run_training_job(type_enum, batch_id, prediction_enum)
            logger.info(
                "model_train_job_completed",
                type=type_enum.value,
                prediction_type=prediction_enum.value,
                batch=batch_id,
            )
        except Exception as e:
            logger.error(
                "model_train_job_failed",
                type=type_enum.value,
                prediction_type=prediction_enum.value,
                batch=batch_id,
                error=str(e),
            )
            raise
        finally:
            logging.unbind_job_context()
