"""
Author: Sean Froning
Created Date: 5.9.2026
Database persistence for prediction inference
"""
from typing import Optional
from psycopg2 import sql  # pyright: ignore[reportMissingModuleSource]
from focus_python import db_pool, logging  # pyright: ignore[reportMissingImports]
from focus_python import (  # pyright: ignore[reportMissingImports]
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
