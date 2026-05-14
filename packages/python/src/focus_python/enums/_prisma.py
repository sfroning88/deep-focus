"""
Author: Sean Froning
Created Date: 5.11.2026
Class definitions for Prisma enums
"""

from __future__ import annotations
from enum import Enum
from .prediction import PredictionType


class PrismaPredictionType(str, Enum):
    CONTROLLABLE_PRD = "controllablePrd"

    @classmethod
    def cast(cls, domain: PredictionType | None) -> PrismaPredictionType:
        if domain is None:
            raise ValueError("prediction type is required")
        return cls[domain.name]
