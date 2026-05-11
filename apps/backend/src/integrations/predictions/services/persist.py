"""
Author: Sean Froning
Created Date: 5.9.2026
Database persistence for prediction inference
"""
from datetime import date, datetime
from typing import Optional
from psycopg2 import sql  # pyright: ignore[reportMissingModuleSource]
from focus_python import db_pool, logging  # pyright: ignore[reportMissingImports]
from focus_python import (  # pyright: ignore[reportMissingImports]
    PROPERTY_SNAPSHOT_TABLE,
    PROPERTY_TABLE,
    Property,
)

logger = logging.get_logger(__name__)


class PersistServices:
    """Database persistence for inference"""

    @staticmethod
    def fetch_property(property_id: str) -> Optional[Property]:
        """Pull a single property row by id and hydrate a Property pydantic model"""
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
            WHERE id = %s::uuid
            LIMIT 1
        """).format(
            table=sql.Identifier(*PROPERTY_TABLE)
        )
        with db_pool.get_cursor() as cursor:
            query_string = query.as_string(cursor)
        row = db_pool.execute_query(query_string, (property_id,), fetch_one=True)
        if not row:
            return None
        return Property(**row)

    @staticmethod
    def fetch_latest_snapshot_reported_at(property_id: str) -> Optional[date]:
        """Latest snapshot reported_at for the property (matches training snapshot_date feature)."""
        query = sql.SQL("""
            SELECT reported_at::date AS reported_at
            FROM {table}
            WHERE property_id = %s::uuid
            ORDER BY reported_at DESC
            LIMIT 1
        """).format(
            table=sql.Identifier(*PROPERTY_SNAPSHOT_TABLE)
        )
        with db_pool.get_cursor() as cursor:
            query_string = query.as_string(cursor)
        row = db_pool.execute_query(query_string, (property_id,), fetch_one=True)
        if not row:
            return None
        raw = row.get("reported_at")
        if raw is None:
            return None
        if isinstance(raw, datetime):
            return raw.date()
        return raw
