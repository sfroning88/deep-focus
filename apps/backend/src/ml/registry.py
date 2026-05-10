"""
Author: Sean Froning
Created Date: 5.9.2026
Inference-side cache of trained sklearn models pulled from S3
"""
import threading
from typing import Any, Dict, List, Optional
from focus_python import db_pool, logging  # pyright: ignore[reportMissingImports]
from focus_python import (  # pyright: ignore[reportMissingImports]
    ModelStorageServices,
    TRAINING_BATCH_TABLE,
    TRAINING_MODEL_TABLE,
    TrainingStatus,
)

logger = logging.get_logger(__name__)

WINNER_KEY = "winner"


class ModelRegistry:
    """In-memory cache of trained sklearn models keyed by TrainingType, plus the winner"""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._models: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._batch_id: Optional[str] = None

    def load(self) -> None:
        """Resolve latest completed batch and pull each model's pkl into the cache"""
        with self._lock:
            try:
                latest = self._fetch_latest_batch()
            except Exception as e:
                logger.error("registry_lookup_failed", error=str(e))
                return
            if not latest:
                logger.info("registry_no_completed_batch")
                self._models, self._metadata, self._batch_id = {}, {}, None
                return

            models: Dict[str, Any] = {}
            metadata: Dict[str, Dict[str, Any]] = {}
            winner_type: Optional[str] = None
            for row in latest["models"]:
                model_type = row["type"]
                try:
                    payload = ModelStorageServices.load(row["storage_path"])
                except Exception as e:
                    logger.error("registry_load_failed", type=model_type, key=row["storage_path"], error=str(e))
                    continue
                models[model_type] = payload["model"]
                metadata[model_type] = {
                    "score": float(row["score"]),
                    "rmse": float(row["rmse"]),
                    "trained_at": row["trained_at"],
                    "msa_encoder": payload.get("msa_encoder"),
                    "feature_columns": payload.get("feature_columns"),
                    "target_column": payload.get("target_column"),
                    "samples": payload.get("samples"),
                    "batch_id": latest["batch_id"],
                    "winner": bool(row["winner"]),
                }
                if row["winner"]:
                    winner_type = model_type

            if winner_type:
                models[WINNER_KEY] = models[winner_type]
                metadata[WINNER_KEY] = {**metadata[winner_type], "winner_type": winner_type}

            self._models = models
            self._metadata = metadata
            self._batch_id = latest["batch_id"]
            logger.info("registry_loaded", batch=latest["batch_id"], count=len(models), winner=winner_type)

    def get(self, model_type: str = WINNER_KEY) -> Any:
        """Return cached model or raise if missing"""
        with self._lock:
            model = self._models.get(model_type)
        if model is None:
            raise RuntimeError(f"Model '{model_type}' not loaded in registry")
        return model

    def get_metadata(self, model_type: str = WINNER_KEY) -> Dict[str, Any]:
        """Return cached metadata for model_type"""
        with self._lock:
            return dict(self._metadata.get(model_type) or {})

    def is_ready(self) -> bool:
        """True if a winner model is currently cached"""
        with self._lock:
            return WINNER_KEY in self._models

    def loaded_model_types(self) -> List[str]:
        """Concrete TrainingType keys currently cached (excludes the WINNER_KEY alias)"""
        with self._lock:
            return [key for key in self._models.keys() if key != WINNER_KEY]

    @staticmethod
    def _fetch_latest_batch() -> Optional[Dict[str, Any]]:
        """Most recent completed batch with its associated completed model rows"""
        batch_schema, batch_table = TRAINING_BATCH_TABLE
        model_schema, model_table = TRAINING_MODEL_TABLE
        batch_row: Optional[Dict[str, Any]] = db_pool.execute_query(
            f"""
            SELECT id::text AS id
            FROM {batch_schema}.{batch_table}
            WHERE status = %s::{batch_schema}.training_status
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (TrainingStatus.COMPLETED.value,),
            fetch_one=True,
        )
        if not batch_row:
            return None
        models: List[Dict[str, Any]] = db_pool.execute_query(
            f"""
            SELECT type::text AS type, storage_path, score, rmse, winner, trained_at
            FROM {model_schema}.{model_table}
            WHERE batch_id = %s::uuid AND status = %s::{model_schema}.training_status
            """,
            (batch_row["id"], TrainingStatus.COMPLETED.value),
        ) or []
        return {"batch_id": batch_row["id"], "models": models}


registry = ModelRegistry()
