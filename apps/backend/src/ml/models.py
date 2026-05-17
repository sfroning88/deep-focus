"""
Author: Sean Froning
Created Date: 5.14.2026
Inference-side in-memory model
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class LoadedModel(BaseModel):
    """In-memory representation of a loaded sklearn model entry"""

    type: str
    score: float
    rmse: float
    trained_at: datetime
    winner: bool
    batch_id: str
    msa_encoding: Optional[Dict[str, float]] = None
    state_encoding: Optional[Dict[str, float]] = None
    feature_columns: Optional[List[str]] = None
    target_column: Optional[str] = None
    samples: Optional[int] = None
    winner_type: Optional[str] = None
