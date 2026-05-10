"""
Author: Sean Froning
Created Date: 5.9.2026
Class objects for model predictions
"""
from typing import Optional
from ._focus_object import BaseFocus
from ..enums import TrainingType, PredictionType

class Prediction(BaseFocus):
    """Normalized model prediction"""
    type: Optional[PredictionType] = None
    result: Optional[float] = None
    feedback_score: Optional[float] = None
    model_type: Optional[TrainingType] = None
    model_batch_id: Optional[str] = None
    property_id: Optional[str] = None
