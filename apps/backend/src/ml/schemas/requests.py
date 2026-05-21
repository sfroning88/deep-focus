"""
Author: Sean Froning
Modified Date: 5.21.2026
Request models for Models
"""

from pydantic import BaseModel


class ModelRequest(BaseModel):
    """Request model for reloading model registry"""

    multi_enabled: bool = False
