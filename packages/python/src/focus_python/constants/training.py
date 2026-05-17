"""
Author: Sean Froning
Modified Date: 5.16.2026
Definitions for training structures
"""

from typing import List
from ..enums import TrainingType

ACUITY_FEATURE_COLUMNS: List[str] = ["pct_cottage", "pct_il", "pct_al", "pct_mc"]
MSA_FEATURE_COLUMN: str = "msa_id_encoded"
MSA_POPULATION_COLUMN: str = "msa_population"
MSA_UNKNOWN: str = "unknown"
STATE_FEATURE_COLUMN: str = "state_encoded"
STATE_UNKNOWN: str = "unknown"
SNAPSHOT_DATE_COLUMN: str = "snapshot_date"
TOTAL_UNITS_COLUMN: str = "total_units"
UNIT_SIZE_COLUMN: str = "unit_size"
BEDS_PER_UNIT_COLUMN: str = "beds_per_unit"
YEAR_BUILT_COLUMN: str = "year_built"
YEARS_SINCE_RENOVATION_COLUMN: str = "years_since_renovation"
FEATURE_COLUMNS: List[str] = [
    *ACUITY_FEATURE_COLUMNS,
    BEDS_PER_UNIT_COLUMN,
    MSA_FEATURE_COLUMN,
    MSA_POPULATION_COLUMN,
    SNAPSHOT_DATE_COLUMN,
    STATE_FEATURE_COLUMN,
    TOTAL_UNITS_COLUMN,
    UNIT_SIZE_COLUMN,
    YEAR_BUILT_COLUMN,
    YEARS_SINCE_RENOVATION_COLUMN,
]
FUNCTION_WEIGHT_SPLITS: List[float] = [0.70, 0.15, 0.15]
TRAINING_JOBS = {
    "linear": TrainingType.LINEAR,
    "ridge": TrainingType.RIDGE,
    "forest": TrainingType.FOREST,
    "gbm": TrainingType.GBM,
}
TRAINING_FEATURE_SCHEMA_VERSION = 6
TRAINING_FUNCTION_SPLIT_VERSION = 1
TRAINING_SPLIT_SEED = 42
TRAINING_MIN_SPLIT_SAMPLES = 5
TRAINING_RIDGE_ALPHA = 1.0
TRAINING_N_ESTIMATORS = 200
TRAINING_ERROR_MSG_MAX_LENGTH = 2000
TRAINING_MSA_ENCODING_TABLE = ("ai", "training_msa_encoding")
TRAINING_FEATURE_TABLE = ("ai", "training_feature")
TRAINING_SPLIT_TABLE = ("ai", "training_split")
TRAINING_BATCH_TABLE = ("ai", "training_batch")
TRAINING_MODEL_TABLE = ("ai", "training_model")
TRAINING_STATUS_ENUM = ("ai", "training_status")
TRAINING_TYPE_ENUM = ("ai", "training_type")
TRAINING_FUNCTION_ENUM = ("ai", "training_function")
TRAINING_MODEL_BUCKET = "models"
