"""
Author: Sean Froning
Modified Date: 5.14.2026
Definitions for training structures
"""

from typing import List
from ..enums import TrainingType

ACUITY_FEATURE_COLUMNS: List[str] = ["pct_cottage", "pct_il", "pct_al", "pct_mc"]
MSA_FEATURE_COLUMN: str = "msa_id_encoded"
MSA_UNKNOWN: str = "unknown"
SNAPSHOT_DATE_COLUMN: str = "snapshot_date"
FEATURE_COLUMNS: List[str] = [
    *ACUITY_FEATURE_COLUMNS,
    MSA_FEATURE_COLUMN,
    SNAPSHOT_DATE_COLUMN,
]
TRAINING_JOBS = {
    "linear": TrainingType.LINEAR,
    "ridge": TrainingType.RIDGE,
    "forest": TrainingType.FOREST,
    "gbm": TrainingType.GBM,
}
TRAINING_FEATURE_SCHEMA_VERSION = 3
TRAINING_SPLIT_SEED = 42
TRAINING_TEST_SPLIT = 0.2
TRAINING_MIN_SPLIT_SAMPLES = 5
TRAINING_RIDGE_ALPHA = 1.0
TRAINING_N_ESTIMATORS = 200
TRAINING_ERROR_MSG_MAX_LENGTH = 2000
TRAINING_MSA_ENCODING_TABLE = ("ai", "training_msa_encoding")
TRAINING_FEATURE_TABLE = ("ai", "training_feature")
TRAINING_BATCH_TABLE = ("ai", "training_batch")
TRAINING_MODEL_TABLE = ("ai", "training_model")
TRAINING_STATUS_ENUM = ("ai", "training_status")
TRAINING_TYPE_ENUM = ("ai", "training_type")
TRAINING_MODEL_BUCKET = "models"
