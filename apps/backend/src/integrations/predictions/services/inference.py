"""
Author: Sean Froning
Created Date: 5.9.2026
Processing functions for model inference
"""

from datetime import date
from typing import List, Optional
from focus_python import logging
from focus_python import (
    Prediction,
    PredictionType,
    Property,
    TrainingType,
)
from ml import (
    Features,
    WINNER_KEY,
    model_registry,
)
from .persist import PersistServices

logger = logging.get_logger(__name__)


class InferenceServices:
    """Operations pertaining to model inference"""

    @staticmethod
    def predict(
        property_id: str,
        multi_enabled: bool = False,
        prediction_type: PredictionType = PredictionType.CONTROLLABLE_PRD,
    ) -> List[Prediction]:
        """Run the latest winning model (or every model in the latest batch) for a property"""
        if not model_registry.is_ready():
            model_registry.load()
        if not model_registry.is_ready():
            raise RuntimeError("No trained model available")

        prop = PersistServices.fetch_property(property_id)
        if prop is None:
            raise ValueError(f"Property '{property_id}' not found")

        snapshot_reported_at = PersistServices.fetch_latest_snapshot_reported_at(
            property_id
        )
        if snapshot_reported_at is None:
            logger.warning(
                "inference_missing_snapshot_date",
                property_id=property_id,
                detail="Using UTC calendar date for snapshot_date feature",
            )

        if multi_enabled:
            keys = model_registry.loaded_model_types()
            return [
                InferenceServices._run(prop, key, prediction_type, snapshot_reported_at)
                for key in keys
            ]
        return [
            InferenceServices._run(
                prop, WINNER_KEY, prediction_type, snapshot_reported_at
            )
        ]

    @staticmethod
    def _run(
        prop: Property,
        model_key: str,
        prediction_type: PredictionType,
        snapshot_reported_at: Optional[date],
    ) -> Prediction:
        """Single-model inference path: load encoding, build vector, predict, package response"""
        model = model_registry.get(model_key)
        meta = model_registry.get_metadata(model_key)
        encoding = meta.get("msa_encoding")
        if encoding is None:
            raise RuntimeError(f"Model '{model_key}' missing msa_encoding metadata")

        X = Features.build_predict_vector(prop, encoding, snapshot_reported_at)
        result = float(model.predict(X)[0])

        resolved_type = meta.get("winner_type") or model_key
        logger.info(
            "model_predicted",
            property_id=prop.id,
            model_type=resolved_type,
            batch=meta.get("batch_id"),
            result=round(result, 2),
        )
        return Prediction(
            type=prediction_type,
            result=result,
            model_type=TrainingType(resolved_type),
            model_batch_id=meta.get("batch_id"),
            property_id=prop.id,
        )
