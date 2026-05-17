"""
Author: Sean Froning
Modified Date: 5.16.2026
Model inference feature engineering
"""

from datetime import date, datetime, timezone
from math import isnan
from typing import Dict, Optional
import numpy as np
import pandas as pd
from focus_python import (
    BEDS_PER_UNIT_COLUMN,
    FEATURE_COLUMNS,
    MSA_FEATURE_COLUMN,
    MSA_POPULATION_COLUMN,
    MSA_UNKNOWN,
    SNAPSHOT_DATE_COLUMN,
    STATE_FEATURE_COLUMN,
    STATE_UNKNOWN,
    TOTAL_UNITS_COLUMN,
    UNIT_SIZE_COLUMN,
    YEAR_BUILT_COLUMN,
    YEARS_SINCE_RENOVATION_COLUMN,
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
        state_encoding: Dict[str, float],
        snapshot_reported_at: Optional[date] = None,
    ) -> pd.DataFrame:
        """Build a single-row inference DataFrame matching FEATURE_COLUMNS"""
        ref_date = snapshot_reported_at or datetime.now(timezone.utc).date()
        ref_ordinal = ref_date.toordinal()

        msa_value = str(prop.msa_id or MSA_UNKNOWN)
        msa_encoded = msa_encoding.get(msa_value, msa_encoding.get(MSA_UNKNOWN, 0.0))

        state_value = prop.state.value if prop.state else STATE_UNKNOWN
        state_encoded = state_encoding.get(
            state_value, state_encoding.get(STATE_UNKNOWN, 0.0)
        )

        total_units = NumberUtils._to_float(prop.total_units) or 0.0
        total_beds = NumberUtils._to_float(prop.total_beds)
        beds_per_unit = (
            total_beds / total_units
            if total_units > 0 and total_beds is not None
            else 0.0
        )

        year_built = NumberUtils._to_float(prop.year_built)
        year_renovated = NumberUtils._to_float(prop.year_renovated)
        years_since_renovation = (
            ref_ordinal - year_renovated
            if not isnan(year_renovated)
            else ref_ordinal - year_built if not isnan(year_built) else 0.0
        )

        row = {
            **NICUtils._acuity_mix(prop),
            BEDS_PER_UNIT_COLUMN: beds_per_unit,
            MSA_FEATURE_COLUMN: msa_encoded,
            MSA_POPULATION_COLUMN: NumberUtils._to_float(prop.msa_population) or 0.0,
            SNAPSHOT_DATE_COLUMN: ref_ordinal,
            STATE_FEATURE_COLUMN: state_encoded,
            TOTAL_UNITS_COLUMN: total_units,
            UNIT_SIZE_COLUMN: NumberUtils._to_float(prop.unit_size) or 0.0,
            YEAR_BUILT_COLUMN: year_built or 0.0,
            YEARS_SINCE_RENOVATION_COLUMN: years_since_renovation,
        }
        return pd.DataFrame([row], columns=FEATURE_COLUMNS).astype(np.float64)
