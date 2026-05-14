"""
Author: Sean Froning
Modified Date: 5.14.2026
Class objects for training runs
"""

from datetime import datetime
from typing import List, Optional
from ._base_focus import BaseFocus
from ..enums import TrainingType, TrainingStatus


class TrainingFeature(BaseFocus):
    """Normalized model training feature"""

    columns: Optional[List[str]] = None
    target: Optional[str] = None
    classes: Optional[List[str]] = None
    schema_version: Optional[int] = None
    batch_id: Optional[str] = None


class TrainingBatch(BaseFocus):
    """Normalized model training batch"""

    status: Optional[TrainingStatus] = None
    samples: Optional[int] = None
    split_seed: Optional[int] = None
    feature: Optional[TrainingFeature] = None


class TrainingModel(BaseFocus):
    """Normalized model training run"""

    type: Optional[TrainingType] = None
    status: Optional[TrainingStatus] = None
    r2_score: Optional[float] = None
    train_score: Optional[float] = None
    rmse: Optional[float] = None
    winner: Optional[bool] = None
    storage_path: Optional[str] = None
    trained_at: Optional[datetime] = None
    error_message: Optional[str] = None
    batch_id: Optional[str] = None
