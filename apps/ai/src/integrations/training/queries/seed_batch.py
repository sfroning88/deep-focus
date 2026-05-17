from psycopg2 import sql
from focus_python import TRAINING_STATUS_ENUM, TRAINING_BATCH_TABLE

QUERY = sql.SQL("""
    INSERT INTO {table}
        (
            id,
            status,
            samples,
            split_seed,
            split_version,
            updated_at
        )
    VALUES
        (%s::uuid, %s::{status_enum}, %s, %s, %s, NOW())
""").format(
    table=sql.Identifier(*TRAINING_BATCH_TABLE),
    status_enum=sql.Identifier(*TRAINING_STATUS_ENUM),
)
