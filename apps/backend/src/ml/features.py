"""
Author: Sean Froning
Created Date: 5.9.2026
Model inference feature engineering
"""

from datetime import date, datetime, timezone
from typing import Dict, Optional
import numpy as np
import pandas as pd
from focus_python import (
    FEATURE_COLUMNS,
    MSA_FEATURE_COLUMN,
    MSA_UNKNOWN,
    SNAPSHOT_DATE_COLUMN,
    TOTAL_UNITS_COLUMN,
    YEAR_BUILT_COLUMN,
    NICUtils,
    NumberUtils,
    Property,
)


class Features:
    """Feature engineering for property-level inference"""

    @staticmethod
    def build_predict_vector(
        prop: Property,
        msa_encoding: Dict[str, float],
        snapshot_reported_at: Optional[date] = None,
    ) -> pd.DataFrame:
        """Build a single-row inference DataFrame matching FEATURE_COLUMNS"""
        msa_value = str(prop.msa_id or MSA_UNKNOWN)
        encoded = msa_encoding.get(msa_value, msa_encoding.get(MSA_UNKNOWN, 0.0))
        ref_date = snapshot_reported_at or datetime.now(timezone.utc).date()
        row = {
            **NICUtils._acuity_mix(prop),
            MSA_FEATURE_COLUMN: encoded,
            SNAPSHOT_DATE_COLUMN: ref_date.toordinal(),
            TOTAL_UNITS_COLUMN: NumberUtils._to_float(prop.total_units),
            YEAR_BUILT_COLUMN: NumberUtils._to_float(prop.year_built),
        }
        return pd.DataFrame([row], columns=FEATURE_COLUMNS).astype(np.float64)
