"""
Author: Sean Froning
Created Date: 5.9.2026
Class definitions for Training enums
"""

from enum import Enum


class TrainingType(str, Enum):
    """Training model enumeration"""

    LINEAR = "linear"
    RIDGE = "ridge"
    FOREST = "forest"
    GBM = "gbm"


class TrainingStatus(str, Enum):
    """Training status enumeration"""

    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
