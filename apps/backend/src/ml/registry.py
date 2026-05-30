"""
Author: Sean Froning
Modified Date: 5.30.2026
Inference-side cache of trained models
"""

import threading
from typing import Any, Dict, List, Optional
from focus_python import db_pool, logging
from focus_python import (
    PREDICTION_TARGETS,
    ModelStorageServices,
    PredictionType,
    TrainingStatus,
)
from .models import LoadedModel, PredictionTypeRegistry
from .queries.select_latest_completed_batch import QUERY as SELECT_LATEST_BATCH
from .queries.select_completed_models_by_batch import QUERY as SELECT_MODELS_BY_BATCH
from .queries.select_winner_model_by_batch import QUERY as SELECT_WINNER_BY_BATCH

logger = logging.get_logger(__name__)

WINNER_KEY = "winner"


class ModelRegistry:
    """In-memory cache of trained sklearn models keyed by TrainingType, plus the winner"""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._registries: Dict[str, PredictionTypeRegistry] = {
            prediction_type.value: self._empty_registry()
            for prediction_type in PREDICTION_TARGETS
        }

    @staticmethod
    def _empty_registry() -> PredictionTypeRegistry:
        return PredictionTypeRegistry(
            models={},
            metadata={},
            batch_id=None,
            multi_loaded=False,
        )

    def _ensure_registry(
        self, prediction_type: PredictionType
    ) -> PredictionTypeRegistry:
        """Return the per-type registry slot, creating it if missing."""
        key = prediction_type.value
        reg = self._registries.get(key)
        if reg is None:
            reg = self._empty_registry()
            self._registries[key] = reg
        return reg

    def load(
        self,
        prediction_type: PredictionType,
        multi_enabled: bool = False,
        force: bool = False,
    ) -> None:
        """Idempotently resolve the latest batch and pull model(s) into the cache"""
        try:
            batch_id, rows = self._fetch_latest_batch(prediction_type)
        except Exception as err:
            logger.error("registry_lookup_failed", error=str(err))
            raise RuntimeError(f"Model registry lookup failed: {str(err)}")

        if batch_id is None:
            logger.info("registry_no_completed_batch")
            with self._lock:
                reg = self._ensure_registry(prediction_type)
                reg.models, reg.metadata, reg.batch_id = {}, {}, None
                reg.multi_loaded = False
            return

        with self._lock:
            reg = self._ensure_registry(prediction_type)
            already_current = batch_id == reg.batch_id
            already_sufficient = not multi_enabled or reg.multi_loaded
            if not force and already_current and already_sufficient:
                logger.debug("registry_already_current", batch=batch_id)
                return

            if not multi_enabled:
                winner_row = self._fetch_winner_model(batch_id)
                if winner_row is None:
                    logger.warning("registry_no_winner", batch=batch_id)
                    reg.models, reg.metadata, reg.batch_id = {}, {}, None
                    reg.multi_loaded = False
                    return
                rows = [winner_row]

            self._commit_loaded_rows(rows, batch_id, multi_enabled, prediction_type)

    def _commit_loaded_rows(
        self,
        rows: List[Dict[str, Any]],
        batch_id: str,
        multi_enabled: bool,
        prediction_type: PredictionType,
    ) -> None:
        """Build estimator/metadata dicts from rows, wire winner alias, and commit to state"""
        estimators: Dict[str, Any] = {}
        metadata: Dict[str, LoadedModel] = {}
        for row in rows:
            entry, estimator = self._load_model_entry(row, batch_id)
            if entry is None or estimator is None:
                continue
            estimators[entry.type] = estimator
            metadata[entry.type] = entry

        winner_type = self._resolve_winner(metadata)
        if winner_type:
            estimators[WINNER_KEY] = estimators[winner_type]
            metadata[WINNER_KEY] = metadata[winner_type].model_copy(
                update={"winner_type": winner_type}
            )

        reg = self._ensure_registry(prediction_type)

        reg.models = estimators
        reg.metadata = metadata
        reg.batch_id = batch_id
        reg.multi_loaded = multi_enabled
        logger.info(
            "registry_loaded",
            batch=batch_id,
            count=len(estimators),
            winner=winner_type,
        )

    def get(self, prediction_type: PredictionType, model_type: str = WINNER_KEY) -> Any:
        """Return cached sklearn estimator or raise if missing"""
        with self._lock:
            reg = self._ensure_registry(prediction_type)
            estimator = reg.models.get(model_type)
        if estimator is None:
            raise RuntimeError(
                f"Model '{model_type}' not loaded for '{prediction_type}"
            )
        return estimator

    def get_metadata(
        self, prediction_type: PredictionType, model_type: str = WINNER_KEY
    ) -> Dict[str, Any]:
        """Return cached metadata for model_type"""
        with self._lock:
            reg = self._ensure_registry(prediction_type)
            entry = reg.metadata.get(model_type)
        return entry.model_dump() if entry else {}

    def is_ready(self, prediction_type: PredictionType) -> bool:
        """True if a winner model is currently cached"""
        with self._lock:
            reg = self._ensure_registry(prediction_type)
            return WINNER_KEY in reg.models

    def loaded_model_types(self, prediction_type: PredictionType) -> List[str]:
        """Concrete TrainingType keys currently cached (excludes the WINNER_KEY alias)"""
        with self._lock:
            reg = self._ensure_registry(prediction_type)
            return [key for key in reg.models.keys() if key != WINNER_KEY]

    def _load_model_entry(
        self, row: Dict[str, Any], batch_id: str
    ) -> tuple[Optional[LoadedModel], Optional[Any]]:
        """Load one S3 artifact; returns (LoadedModel, estimator) or (None, None) on failure"""
        model_type = row["type"]
        try:
            payload = ModelStorageServices.load(row["storage_path"])
        except Exception as err:
            logger.error(
                "registry_load_failed",
                type=model_type,
                key=row["storage_path"],
                error=str(err),
            )
            return None, None
        msa_encoding = payload.get("msa_encoding")
        if not isinstance(msa_encoding, dict) or not msa_encoding:
            logger.error(
                "registry_payload_missing_msa_encoding",
                type=model_type,
                key=row["storage_path"],
            )
            return None, None
        state_encoding = payload.get("state_encoding")
        if not isinstance(state_encoding, dict) or not state_encoding:
            logger.error(
                "registry_payload_missing_state_encoding",
                type=model_type,
                key=row["storage_path"],
            )
            return None, None
        global_mean = payload.get("global_mean")
        entry = LoadedModel(
            type=model_type,
            score=float(row["r2_score"]),
            rmse=float(row["rmse"]),
            trained_at=row["trained_at"],
            winner=bool(row["winner"]),
            batch_id=batch_id,
            msa_encoding=msa_encoding,
            state_encoding=state_encoding,
            global_mean=float(global_mean) if global_mean is not None else None,
            feature_columns=payload.get("feature_columns"),
            target_column=payload.get("target_column"),
            samples=payload.get("samples"),
        )
        estimator = payload.get("model")
        if estimator is None:
            logger.error(
                "registry_payload_missing_model",
                type=model_type,
                key=row["storage_path"],
            )
            return None, None
        return entry, estimator

    @staticmethod
    def _resolve_winner(metadata: Dict[str, LoadedModel]) -> Optional[str]:
        """Return the model_type marked as winner, or None"""
        return next(
            (model_type for model_type, model in metadata.items() if model.winner), None
        )

    @staticmethod
    def _fetch_latest_batch(
        prediction_type: PredictionType,
    ) -> tuple[Optional[str], List[Dict[str, Any]]]:
        """Return (batch_id, model_rows) for the most recent completed batch"""
        with db_pool.get_cursor() as cursor:
            batch_query = SELECT_LATEST_BATCH.as_string(cursor)
        batch_row: Optional[Dict[str, Any]] = db_pool.execute_query(
            batch_query,
            (
                TrainingStatus.COMPLETED.value,
                prediction_type.value,
            ),
            fetch_one=True,
        )
        if not batch_row:
            return None, []
        with db_pool.get_cursor() as cursor:
            models_query = SELECT_MODELS_BY_BATCH.as_string(cursor)
        models: List[Dict[str, Any]] = (
            db_pool.execute_query(
                models_query,
                (batch_row["id"], TrainingStatus.COMPLETED.value),
            )
            or []
        )
        return batch_row["id"], models

    @staticmethod
    def _fetch_winner_model(batch_id: str) -> Optional[Dict[str, Any]]:
        """Return the single winner model row for a batch, or None"""
        with db_pool.get_cursor() as cursor:
            query = SELECT_WINNER_BY_BATCH.as_string(cursor)
        return db_pool.execute_query(
            query,
            (batch_id, TrainingStatus.COMPLETED.value),
            fetch_one=True,
        )


registry = ModelRegistry()
