"""
Author: Sean Froning
Modified Date: 5.14.2026
Model training feature engineering
"""

from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from focus_python import (
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
from .models import TrainingFrame


class Features:
    """Feature engineering for snapshot-level training"""

    @staticmethod
    def build_training_dataframe(
        properties: List[Property],
        snapshots: List[PropertySnapshot],
        prediction_type: PredictionType,
    ) -> TrainingFrame:
        """Join each snapshot with its property features; one sample per snapshot"""
        if not properties or not snapshots:
            raise ValueError("Properties and snapshots are required for training")

        target = PREDICTION_TARGETS[prediction_type]

        snap_df = Features._build_snapshot_df(snapshots, target)
        prop_df = Features._build_property_df(properties)

        df = prop_df.merge(snap_df, on="property_id", how="inner")
        if df.empty:
            raise ValueError("No overlapping properties + snapshots after join")

        df, msa_encoder = Features._encode_msa(df)

        return TrainingFrame(
            X=df[FEATURE_COLUMNS].astype(np.float64),
            y=df[target].astype(np.float64),
            groups=df["property_id"],
            msa_encoder=msa_encoder,
            target=target,
        )

    @staticmethod
    def _build_snapshot_df(
        snapshots: List[PropertySnapshot], target: str
    ) -> pd.DataFrame:
        """Build and clean the snapshot-side dataframe for a given target column"""
        df = pd.DataFrame(
            [
                {
                    "property_id": s.property_id,
                    target: NumberUtils._to_float(getattr(s, target, None)),
                    SNAPSHOT_DATE_COLUMN: (
                        s.reported_at.toordinal() if s.reported_at else None
                    ),
                }
                for s in snapshots
            ]
        )
        df = df.dropna(subset=[target, SNAPSHOT_DATE_COLUMN])
        return df[df[target] > 0]

    @staticmethod
    def _build_property_df(properties: List[Property]) -> pd.DataFrame:
        """Build the property-side dataframe with MSA and acuity mix columns"""
        return pd.DataFrame(
            [
                {
                    "property_id": p.id,
                    "msa_id": p.msa_id or MSA_UNKNOWN,
                    **NICUtils._acuity_mix(p),
                }
                for p in properties
            ]
        )

    @staticmethod
    def _encode_msa(df: pd.DataFrame) -> Tuple[pd.DataFrame, LabelEncoder]:
        """Fit and apply a LabelEncoder to the msa_id column"""
        encoder = LabelEncoder()
        df = df.copy()
        df[MSA_FEATURE_COLUMN] = encoder.fit_transform(df["msa_id"].astype(str))
        return df, encoder
