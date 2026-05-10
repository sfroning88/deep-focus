"""
Author: Sean Froning
Created Date: 5.9.2026
Definitions for prediction structures
"""
from typing import Dict
from ..enums import PredictionType

PREDICTION_TARGETS: Dict[PredictionType, str] = {
    PredictionType.CONTROLLABLE_PRD: "controllable_prd",
}
PREDICTION_TABLE = ("ai", "prediction")
