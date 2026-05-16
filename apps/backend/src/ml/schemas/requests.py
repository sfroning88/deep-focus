"""
Author: Sean Froning
Created Date: 5.16.2026
Request models for Models
"""

from pydantic import BaseModel, ConfigDict


class ModelRequest(BaseModel):
    """Request model for reloading model registry (empty body)"""

    model_config = ConfigDict(extra="forbid")
