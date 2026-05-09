"""
Author: Sean Froning
Created Date: 5.9.2026
Processing functions for model inference
"""
from typing import List
from focus_python import logging  # pyright: ignore[reportMissingImports]
from focus_python import (  # pyright: ignore[reportMissingImports]
    Prediction,
    PredictionType,
    Property,
    TrainingType,
)
from ml import Features, WINNER_KEY, model_registry  # pyright: ignore[reportMissingImports]
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

        if multi_enabled:
            keys = model_registry.loaded_model_types()
            return [InferenceServices._run(prop, key, prediction_type) for key in keys]
        return [InferenceServices._run(prop, WINNER_KEY, prediction_type)]

    @staticmethod
    def _run(prop: Property, model_key: str, prediction_type: PredictionType) -> Prediction:
        """Single-model inference path: load encoder, build vector, predict, package response"""
        model = model_registry.get(model_key)
        meta = model_registry.get_metadata(model_key)
        encoder = meta.get("msa_encoder")
        if encoder is None:
            raise RuntimeError(f"Model '{model_key}' missing msa_encoder metadata")

        X = Features.build_predict_vector(prop, encoder)
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
