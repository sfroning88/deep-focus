from psycopg2 import sql
from focus_python import TRAINING_BATCH_TABLE, TRAINING_STATUS_ENUM

QUERY = sql.SQL("""
    SELECT id::text AS id
    FROM {table}
    WHERE status = %s::{status_enum}
    ORDER BY created_at DESC
    LIMIT 1
""").format(
    table=sql.Identifier(*TRAINING_BATCH_TABLE),
    status_enum=sql.Identifier(*TRAINING_STATUS_ENUM),
)
