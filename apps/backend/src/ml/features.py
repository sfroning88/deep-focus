"""
Author: Sean Froning
Created Date: 5.9.2026
Model inference feature engineering
"""
from datetime import date
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder  # pyright: ignore[reportMissingImports]
from focus_python import (  # pyright: ignore[reportMissingImports]
    FEATURE_COLUMNS,
    MSA_FEATURE_COLUMN,
    MSA_UNKNOWN,
    SNAPSHOT_DATE_COLUMN,
    NICUtils,
    Property,
)


class Features:
    """Feature engineering for property-level inference"""

    @staticmethod
    def build_predict_vector(prop: Property, msa_encoder: LabelEncoder) -> pd.DataFrame:
        """Build a single-row inference DataFrame matching FEATURE_COLUMNS"""
        msa_value = str(prop.msa_id or MSA_UNKNOWN)
        encoded = (
            int(msa_encoder.transform([msa_value])[0])
            if msa_value in set(msa_encoder.classes_)
            else -1
        )
        row = {
            **NICUtils._acuity_mix(prop),
            MSA_FEATURE_COLUMN: encoded,
            SNAPSHOT_DATE_COLUMN: date.today().toordinal(),
        }
        return pd.DataFrame([row], columns=FEATURE_COLUMNS).astype(np.float64)
