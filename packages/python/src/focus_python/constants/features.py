"""
Author: Sean Froning
Created Date: 5.16.2026
Definitions for feature contracts
"""

from typing import List

ACUITY_FEATURE_COLUMNS: List[str] = ["pct_cottage", "pct_il", "pct_al", "pct_mc"]
MSA_FEATURE_COLUMN: str = "msa_id_encoded"
MSA_UNKNOWN: str = "unknown"
SNAPSHOT_DATE_COLUMN: str = "snapshot_date"
TOTAL_UNITS_COLUMN: str = "total_units"
YEAR_BUILT_COLUMN: str = "year_built"
FEATURE_COLUMNS: List[str] = [
    *ACUITY_FEATURE_COLUMNS,
    MSA_FEATURE_COLUMN,
    SNAPSHOT_DATE_COLUMN,
    TOTAL_UNITS_COLUMN,
    YEAR_BUILT_COLUMN,
]
