"""
Author: Sean Froning
Created Date: 5.9.2026
Processing functions for model persistence
"""
from datetime import datetime, timezone
from typing import List
from psycopg2 import sql  # pyright: ignore[reportMissingModuleSource]
from focus_python import db_pool, logging  # pyright: ignore[reportMissingImports]
from focus_python import (  # pyright: ignore[reportMissingImports]
    PROPERTY_SNAPSHOT_TABLE,
    PROPERTY_TABLE,
    TRAINING_JOBS,
    TRAINING_ERROR_MSG_MAX_LENGTH,
    TRAINING_FEATURE_TABLE,
    TRAINING_BATCH_TABLE,
    TRAINING_MODEL_TABLE,
    TRAINING_STATUS_ENUM,
    TRAINING_TYPE_ENUM,
    Property,
    PropertySnapshot,
    TrainingBatch,
    TrainingModel,
    TrainingStatus,
    TrainingType,
)

logger = logging.get_logger(__name__)


class PersistServices:
    """Database persistence for training batches and runs"""

    @staticmethod
    def fetch_properties() -> List[Property]:
        """Pull all property rows and hydrate Property pydantic models"""
        query = sql.SQL("""
            SELECT
                id::text AS id,
                name,
                address,
                city,
                state,
                zip,
                year_built,
                year_renovated,
                unit_size,
                cottage_units,
                independent_units,
                assisted_units,
                memory_units,
                total_units,
                total_beds,
                msa_id::text AS msa_id
            FROM {table}
        """).format(
            table=sql.Identifier(*PROPERTY_TABLE)
        )
        with db_pool.get_cursor() as cursor: queryString = query.as_string(cursor)
        rows = db_pool.execute_query(queryString)
        return [Property(**row) for row in rows]

    @staticmethod
    def fetch_snapshots() -> List[PropertySnapshot]:
        """Pull all property_snapshot rows and hydrate PropertySnapshot pydantic models"""
        query = sql.SQL("""
            SELECT
                property_id::text AS property_id,
                reported_at,
                occupancy,
                total_revenues,
                controllable_expenses,
                controllable_prd
            FROM {table}
        """).format(
            table=sql.Identifier(*PROPERTY_SNAPSHOT_TABLE)
        )
        with db_pool.get_cursor() as cursor: queryString = query.as_string(cursor)
        rows = db_pool.execute_query(queryString)
        return [PropertySnapshot(**row) for row in rows]

    @staticmethod
    def seed_batch(batch: TrainingBatch) -> None:
        """Insert TrainingBatch + TrainingFeature + pending TrainingModel rows atomically"""
        if not batch.feature:
            raise ValueError("seed_batch requires batch.feature")
        feature = batch.feature
        now = datetime.now(tz=timezone.utc)
        batch_query = sql.SQL("""
            INSERT INTO {table}
                (id, status, samples, split_seed, updated_at)
            VALUES
                (%s::uuid, %s::{status_enum}, %s, %s, NOW())
        """).format(
            table=sql.Identifier(*TRAINING_BATCH_TABLE),
            status_enum=sql.Identifier(*TRAINING_STATUS_ENUM),
        )
        feature_query = sql.SQL("""
            INSERT INTO {table}
                (batch_id, columns, target, classes, schema_version, updated_at)
            VALUES
                (%s::uuid, %s, %s, %s, %s, NOW())
        """).format(
            table=sql.Identifier(*TRAINING_FEATURE_TABLE)
        )
        model_query = sql.SQL("""
            INSERT INTO {table}
                (type, status, score, rmse, winner, storage_path, trained_at, batch_id, updated_at)
            VALUES
                (%s::{type_enum}, %s::{status_enum}, 0, 0, false, '', %s, %s::uuid, NOW())
        """).format(
            table=sql.Identifier(*TRAINING_MODEL_TABLE),
            type_enum=sql.Identifier(*TRAINING_TYPE_ENUM),
            status_enum=sql.Identifier(*TRAINING_STATUS_ENUM),
        )
        with db_pool.get_cursor() as cursor:
            cursor.execute(
                batch_query.as_string(cursor),
                (batch.id, TrainingStatus.PENDING.value, batch.samples, batch.split_seed),
            )
            cursor.execute(
                feature_query.as_string(cursor),
                (batch.id, feature.columns, feature.target, feature.classes, feature.schema_version),
            )
            for training_type in TRAINING_JOBS.values():
                cursor.execute(
                    model_query.as_string(cursor),
                    (training_type.value, TrainingStatus.PENDING.value, now, batch.id),
                )

    @staticmethod
    def set_model_executing(training_type: TrainingType, batch_id: str) -> None:
        """Move a pending TrainingModel row into executing state"""
        query = sql.SQL("""
            UPDATE {table}
            SET status = %s::{status_enum}, updated_at = NOW()
            WHERE type = %s::{type_enum} AND batch_id = %s::uuid
        """).format(
            table=sql.Identifier(*TRAINING_MODEL_TABLE),
            status_enum=sql.Identifier(*TRAINING_STATUS_ENUM),
            type_enum=sql.Identifier(*TRAINING_TYPE_ENUM),
        )
        with db_pool.get_cursor() as cursor: queryString = query.as_string(cursor)
        db_pool.execute_query(
            queryString,
            (TrainingStatus.EXECUTING.value, training_type.value, batch_id),
        )

    @staticmethod
    def bump_batch_executing(batch_id: str) -> None:
        """Move TrainingBatch from pending → executing the first time a worker starts"""
        query = sql.SQL("""
            UPDATE {table}
            SET status = %s::{status_enum}, updated_at = NOW()
            WHERE id = %s::uuid AND status = %s::{status_enum}
        """).format(
            table=sql.Identifier(*TRAINING_BATCH_TABLE),
            status_enum=sql.Identifier(*TRAINING_STATUS_ENUM),
        )
        with db_pool.get_cursor() as cursor: queryString = query.as_string(cursor)
        db_pool.execute_query(
            queryString,
            (TrainingStatus.EXECUTING.value, batch_id, TrainingStatus.PENDING.value),
        )

    @staticmethod
    def set_model_completed(model: TrainingModel) -> None:
        """Persist successful training run metrics + storage location"""
        query = sql.SQL("""
            UPDATE {table}
            SET status = %s::{status_enum},
                score = %s,
                rmse = %s,
                storage_path = %s,
                trained_at = %s,
                error_message = NULL,
                updated_at = NOW()
            WHERE type = %s::{type_enum} AND batch_id = %s::uuid
        """).format(
            table=sql.Identifier(*TRAINING_MODEL_TABLE),
            status_enum=sql.Identifier(*TRAINING_STATUS_ENUM),
            type_enum=sql.Identifier(*TRAINING_TYPE_ENUM),
        )
        with db_pool.get_cursor() as cursor: queryString = query.as_string(cursor)
        db_pool.execute_query(
            queryString,
            (
                TrainingStatus.COMPLETED.value,
                float(model.score),
                float(model.rmse),
                model.storage_path,
                model.trained_at,
                model.type.value,
                model.batch_id,
            ),
        )

    @staticmethod
    def set_model_failed(model: TrainingModel) -> None:
        """Mark a training run as failed and capture the error for debugging"""
        truncated = (model.error_message or "")[:TRAINING_ERROR_MSG_MAX_LENGTH]
        query = sql.SQL("""
            UPDATE {table}
            SET status = %s::{status_enum},
                error_message = %s,
                updated_at = NOW()
            WHERE type = %s::{type_enum} AND batch_id = %s::uuid
        """).format(
            table=sql.Identifier(*TRAINING_MODEL_TABLE),
            status_enum=sql.Identifier(*TRAINING_STATUS_ENUM),
            type_enum=sql.Identifier(*TRAINING_TYPE_ENUM),
        )
        with db_pool.get_cursor() as cursor: queryString = query.as_string(cursor)
        db_pool.execute_query(
            queryString,
            (TrainingStatus.FAILED.value, truncated, model.type.value, model.batch_id),
        )

    @staticmethod
    def finalize_batch(batch_id: str) -> None:
        """Resolve batch terminal state + winner based on child model rows"""
        select_query = sql.SQL("""
            SELECT type::text AS type, status::text AS status, score
            FROM {table}
            WHERE batch_id = %s::uuid
        """).format(
            table=sql.Identifier(*TRAINING_MODEL_TABLE)
        )
        with db_pool.get_cursor() as cursor: select_string = select_query.as_string(cursor)
        rows = db_pool.execute_query(select_string, (batch_id,))

        statuses = {row["status"] for row in rows}
        expected_types = {training_type.value for training_type in TrainingType}
        completed_types = {row["type"] for row in rows if row["status"] == TrainingStatus.COMPLETED.value}

        if TrainingStatus.FAILED.value in statuses:
            fail_query = sql.SQL("""
                UPDATE {table}
                SET status = %s::{status_enum}, updated_at = NOW()
                WHERE id = %s::uuid AND status <> %s::{status_enum}
            """).format(
                table=sql.Identifier(*TRAINING_BATCH_TABLE),
                status_enum=sql.Identifier(*TRAINING_STATUS_ENUM),
            )
            with db_pool.get_cursor() as cursor: fail_string = fail_query.as_string(cursor)
            db_pool.execute_query(
                fail_string,
                (TrainingStatus.FAILED.value, batch_id, TrainingStatus.FAILED.value),
            )
            logger.warning("training_batch_failed", batch=batch_id, statuses=list(statuses))
            return

        if not expected_types.issubset(completed_types):
            return

        winner_row = max(rows, key=lambda row: float(row["score"]))
        winner_type = winner_row["type"]
        winner_query = sql.SQL("""
            UPDATE {table}
            SET winner = (type::text = %s), updated_at = NOW()
            WHERE batch_id = %s::uuid
        """).format(
            table=sql.Identifier(*TRAINING_MODEL_TABLE)
        )
        complete_query = sql.SQL("""
            UPDATE {table}
            SET status = %s::{status_enum}, updated_at = NOW()
            WHERE id = %s::uuid
        """).format(
            table=sql.Identifier(*TRAINING_BATCH_TABLE),
            status_enum=sql.Identifier(*TRAINING_STATUS_ENUM),
        )
        with db_pool.get_cursor() as cursor:
            cursor.execute(winner_query.as_string(cursor), (winner_type, batch_id))
            cursor.execute(complete_query.as_string(cursor), (TrainingStatus.COMPLETED.value, batch_id))
        logger.info(
            "training_batch_completed",
            batch=batch_id,
            winner=winner_type,
            score=float(winner_row["score"]),
        )
