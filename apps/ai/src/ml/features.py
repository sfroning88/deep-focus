"""
Author: Sean Froning
Modified Date: 5.16.2026
Model training feature engineering
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from focus_python import (
    FEATURE_COLUMNS,
    MSA_FEATURE_COLUMN,
    MSA_UNKNOWN,
    SNAPSHOT_DATE_COLUMN,
    TOTAL_UNITS_COLUMN,
    YEAR_BUILT_COLUMN,
    PREDICTION_TARGETS,
    PredictionType,
    Property,
    PropertySnapshot,
    TrainingMSAEncoding,
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

        msa_encoding, msa_records = Features._compute_msa_encoding(df, target)
        global_mean = float(df[target].mean())
        df[MSA_FEATURE_COLUMN] = df["msa_id"].map(msa_encoding).fillna(global_mean)

        return TrainingFrame(
            X=df[FEATURE_COLUMNS].astype(np.float64),
            y=df[target].astype(np.float64),
            groups=df["property_id"],
            msa_id=df["msa_id"].reset_index(drop=True),
            msa_encoding=msa_encoding,
            msa_records=msa_records,
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
                    TOTAL_UNITS_COLUMN: NumberUtils._to_float(p.total_units),
                    YEAR_BUILT_COLUMN: NumberUtils._to_float(p.year_built),
                    **NICUtils._acuity_mix(p),
                }
                for p in properties
            ]
        )

    @staticmethod
    def _compute_msa_encoding(
        df: pd.DataFrame, target: str
    ) -> Tuple[Dict[str, float], List[TrainingMSAEncoding]]:
        """Compute mean target and sample count per msa_id"""
        grouped = df.groupby("msa_id")[target].agg(["mean", "count"])
        encoding = grouped["mean"].to_dict()
        records = [
            TrainingMSAEncoding(
                msa_id=msa_id, mean_target=row["mean"], sample_count=row["count"]
            )
            for msa_id, row in grouped.iterrows()
        ]
        return encoding, records
