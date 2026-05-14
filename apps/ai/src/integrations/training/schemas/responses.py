"""
Author: Sean Froning
Created Date: 5.9.2026
Response models for Training
"""

from pydantic import BaseModel
from typing import List


class TrainingResponse(BaseModel):
    """Response model for running training job"""

    job_ids: List[str]
