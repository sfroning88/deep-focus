"""
Author: Sean Froning
Created Date: 5.9.2026
Class definitions for Prediction enums
"""

from enum import Enum


class PredictionType(str, Enum):
    """Prediction scope enumeration"""

    CONTROLLABLE_PRD = "controllable_prd"
