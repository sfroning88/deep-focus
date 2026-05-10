"""
Author: Sean Froning
Created Date: 5.9.2026
Model training feature engineering
"""
from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder  # pyright: ignore[reportMissingImports]
from focus_python import (  # pyright: ignore[reportMissingImports]
    FEATURE_COLUMNS,
    MSA_FEATURE_COLUMN,
    MSA_UNKNOWN,
    PREDICTION_TARGETS,
    PredictionType,
    Property,
    PropertySnapshot,
    NICUtils,
    NumberUtils,
)


class Features:
    """Feature engineering for property-level training"""

    @staticmethod
    def build_training_dataframe(
        properties: List[Property],
        snapshots: List[PropertySnapshot],
        prediction_type: PredictionType,
    ) -> Tuple[pd.DataFrame, pd.Series, pd.Series, LabelEncoder, str]:
        """Join properties + snapshots, aggregate target per-property, encode MSA"""
        if not properties or not snapshots:
            raise ValueError("Properties and snapshots are required for training")

        target = PREDICTION_TARGETS[prediction_type]

        snap_df = pd.DataFrame([
            {"property_id": s.property_id, target: NumberUtils._to_float(getattr(s, target, None))}
            for s in snapshots
        ])
        snap_df = snap_df.dropna(subset=[target])
        snap_df = snap_df[snap_df[target] > 0]
        target_per_property = snap_df.groupby("property_id")[target].median().reset_index()

        prop_df = pd.DataFrame([
            {"property_id": p.id, "msa_id": p.msa_id or MSA_UNKNOWN, **NICUtils._acuity_mix(p)}
            for p in properties
        ])

        df = prop_df.merge(target_per_property, on="property_id", how="inner")
        if df.empty:
            raise ValueError("No overlapping properties + snapshots after join")

        msa_encoder = LabelEncoder()
        df[MSA_FEATURE_COLUMN] = msa_encoder.fit_transform(df["msa_id"].astype(str))

        X = df[FEATURE_COLUMNS].astype(np.float64)
        y = df[target].astype(np.float64)
        groups = df["property_id"]
        return X, y, groups, msa_encoder, target
