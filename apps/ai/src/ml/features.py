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
    SNAPSHOT_DATE_COLUMN,
    PREDICTION_TARGETS,
    PredictionType,
    Property,
    PropertySnapshot,
    NICUtils,
    NumberUtils,
)


class Features:
    """Feature engineering for snapshot-level training"""

    @staticmethod
    def build_training_dataframe(
        properties: List[Property],
        snapshots: List[PropertySnapshot],
        prediction_type: PredictionType,
    ) -> Tuple[pd.DataFrame, pd.Series, pd.Series, LabelEncoder, str]:
        """Join each snapshot with its property features; one sample per snapshot"""
        if not properties or not snapshots:
            raise ValueError("Properties and snapshots are required for training")

        target = PREDICTION_TARGETS[prediction_type]

        snap_df = pd.DataFrame([
            {
                "property_id": s.property_id,
                target: NumberUtils._to_float(getattr(s, target, None)),
                SNAPSHOT_DATE_COLUMN: s.reported_at.toordinal() if s.reported_at else None,
            }
            for s in snapshots
        ])
        snap_df = snap_df.dropna(subset=[target, SNAPSHOT_DATE_COLUMN])
        snap_df = snap_df[snap_df[target] > 0]

        prop_df = pd.DataFrame([
            {"property_id": p.id, "msa_id": p.msa_id or MSA_UNKNOWN, **NICUtils._acuity_mix(p)}
            for p in properties
        ])

        df = prop_df.merge(snap_df, on="property_id", how="inner")
        if df.empty:
            raise ValueError("No overlapping properties + snapshots after join")

        msa_encoder = LabelEncoder()
        df[MSA_FEATURE_COLUMN] = msa_encoder.fit_transform(df["msa_id"].astype(str))

        X = df[FEATURE_COLUMNS].astype(np.float64)
        y = df[target].astype(np.float64)
        groups = df["property_id"]
        return X, y, groups, msa_encoder, target
