"""
Author: Sean Froning
Created Date: 5.9.2026
Processing functions for model training
"""
import uuid
from datetime import datetime, timezone
from typing import Tuple
import numpy as np 
from sklearn.base import BaseEstimator  # pyright: ignore[reportMissingImports]
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor  # pyright: ignore[reportMissingImports]
from sklearn.linear_model import LinearRegression, Ridge  # pyright: ignore[reportMissingImports]
from sklearn.metrics import mean_squared_error, r2_score  # pyright: ignore[reportMissingImports]
from sklearn.model_selection import GroupShuffleSplit  # pyright: ignore[reportMissingImports]
from focus_python import logging  # pyright: ignore[reportMissingImports]
from focus_python import (  # pyright: ignore[reportMissingImports]
    FEATURE_COLUMNS,
    ModalStorageServices,
    TRAINING_FEATURE_SCHEMA_VERSION,
    TRAINING_SPLIT_SEED,
    TRAINING_TEST_SPLIT,
    TRAINING_MIN_SPLIT_SAMPLES,
    TRAINING_RIDGE_ALPHA,
    TRAINING_N_ESTIMATORS,
    PredictionType,
    TrainingBatch,
    TrainingFeature,
    TrainingModel,
    TrainingStatus,
    TrainingType,
)
from ml import Features  # pyright: ignore[reportMissingImports]
from .persist import PersistServices

logger = logging.get_logger(__name__)


class TrainingServices:
    """Operations pertaining to model training"""

    @staticmethod
    def create_batch(prediction_type: PredictionType = PredictionType.CONTROLLABLE_PRD) -> str:
        """Build feature contract + persist seeded TrainingBatch / TrainingFeature / TrainingModel rows"""
        batch_id = str(uuid.uuid4())
        properties = PersistServices.fetch_properties()
        snapshots = PersistServices.fetch_snapshots()
        if not properties:
            raise ValueError("No properties available for training")
        if not snapshots:
            raise ValueError("No snapshots available for training")

        X, _, _, msa_encoder, target = Features.build_training_dataframe(
            properties, snapshots, prediction_type,
        )
        batch = TrainingBatch(
            id=batch_id,
            status=TrainingStatus.PENDING,
            samples=len(X),
            split_seed=TRAINING_SPLIT_SEED,
            feature=TrainingFeature(
                batch_id=batch_id,
                columns=list(FEATURE_COLUMNS),
                target=target,
                classes=[str(class_label) for class_label in msa_encoder.classes_],
                schema_version=TRAINING_FEATURE_SCHEMA_VERSION,
            ),
        )

        PersistServices.seed_batch(batch)
        logger.info(
            "training_batch_seeded",
            batch=batch_id,
            prediction_type=prediction_type.value,
            target=target,
            samples=batch.samples,
            columns=batch.feature.columns,
            classes_count=len(batch.feature.classes or []),
        )
        return batch_id

    @staticmethod
    def run_training_job(
        training_type: TrainingType,
        batch_id: str,
        prediction_type: PredictionType = PredictionType.CONTROLLABLE_PRD,
    ) -> None:
        """RQ job entrypoint: train a single sklearn model for the given type + batch"""
        logger.info(
            "training_started",
            type=training_type.value,
            prediction_type=prediction_type.value,
            batch=batch_id,
        )
        try:
            PersistServices.bump_batch_executing(batch_id)
            PersistServices.set_model_executing(training_type, batch_id)

            properties = PersistServices.fetch_properties()
            snapshots = PersistServices.fetch_snapshots()
            X, y, groups, msa_encoder, target = Features.build_training_dataframe(
                properties, snapshots, prediction_type,
            )

            estimator = TrainingServices._build_estimator(training_type)
            model, score, rmse = TrainingServices._train_and_score(estimator, X, y, groups)
            samples = len(X)
            logger.info(
                "training_scored",
                type=training_type.value,
                r2=round(score, 4),
                rmse=round(rmse, 2),
                samples=samples,
            )

            trained_at = datetime.now(tz=timezone.utc)
            payload = {
                "model": model,
                "msa_encoder": msa_encoder,
                "feature_columns": list(FEATURE_COLUMNS),
                "target_column": target,
                "prediction_type": prediction_type.value,
                "score": score,
                "rmse": rmse,
                "samples": samples,
                "trained_at": trained_at.isoformat(),
                "type": training_type.value,
                "batch_id": batch_id,
            }
            key = f"{batch_id}/{training_type.value}.pkl"
            storage_path = ModalStorageServices.save(payload, key)

            PersistServices.set_model_completed(TrainingModel(
                type=training_type,
                batch_id=batch_id,
                score=score,
                rmse=rmse,
                storage_path=storage_path,
                trained_at=trained_at,
            ))
        except Exception as e:
            logger.exception("training_job_failed", type=training_type.value, batch=batch_id, error=str(e))
            try:
                PersistServices.set_model_failed(TrainingModel(
                    type=training_type,
                    batch_id=batch_id,
                    error_message=str(e),
                ))
            except Exception as inner:
                logger.error("training_failure_persist_failed", batch=batch_id, error=str(inner))
            try:
                PersistServices.finalize_batch(batch_id)
            except Exception as inner:
                logger.error("training_finalize_failed", batch=batch_id, error=str(inner))
            raise

        try:
            PersistServices.finalize_batch(batch_id)
        except Exception as e:
            logger.error("training_finalize_failed", batch=batch_id, error=str(e))

        logger.info(
            "training_completed",
            type=training_type.value,
            batch=batch_id,
            r2=round(score, 4),
        )

    @staticmethod
    def _build_estimator(training_type: TrainingType) -> BaseEstimator:
        """Map TrainingType enum to a fresh sklearn estimator instance"""
        if training_type == TrainingType.LINEAR:
            return LinearRegression()
        if training_type == TrainingType.RIDGE:
            return Ridge(alpha=TRAINING_RIDGE_ALPHA, random_state=TRAINING_SPLIT_SEED)
        if training_type == TrainingType.FOREST:
            return RandomForestRegressor(
                n_estimators=TRAINING_N_ESTIMATORS,
                random_state=TRAINING_SPLIT_SEED,
                n_jobs=-1,
            )
        if training_type == TrainingType.GBM:
            return GradientBoostingRegressor(
                n_estimators=TRAINING_N_ESTIMATORS,
                random_state=TRAINING_SPLIT_SEED,
            )
        raise ValueError(f"Unsupported training type: {training_type}")

    @staticmethod
    def _train_and_score(estimator: BaseEstimator, X, y, groups) -> Tuple[BaseEstimator, float, float]:
        """Group-aware train/test split with full-data refit; returns model + test metrics"""
        sample_count = len(X)
        if sample_count < TRAINING_MIN_SPLIT_SAMPLES:
            estimator.fit(X, y)
            predictions = estimator.predict(X)
            score = float(r2_score(y, predictions))
            rmse = float(np.sqrt(mean_squared_error(y, predictions)))
            return estimator, score, rmse

        splitter = GroupShuffleSplit(
            n_splits=1,
            test_size=TRAINING_TEST_SPLIT,
            random_state=TRAINING_SPLIT_SEED,
        )
        n_unique_groups = groups.nunique()
        if n_unique_groups * TRAINING_TEST_SPLIT < 2:
            estimator.fit(X, y)
            predictions = estimator.predict(X)
            score = float(r2_score(y, predictions))
            rmse = float(np.sqrt(mean_squared_error(y, predictions)))
            return estimator, score, rmse

        train_indices, test_indices = next(splitter.split(X, y, groups=groups))
        X_train, X_test = X.iloc[train_indices], X.iloc[test_indices]
        y_train, y_test = y.iloc[train_indices], y.iloc[test_indices]
        estimator.fit(X_train, y_train)
        predictions = estimator.predict(X_test)
        score = float(r2_score(y_test, predictions))
        rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
        estimator.fit(X, y)
        return estimator, score, rmse
