from psycopg2 import sql
from focus_python import TRAINING_FEATURE_TABLE

QUERY = sql.SQL("""
    INSERT INTO {table}
        (
            batch_id, 
            columns, 
            target, 
            classes, 
            schema_version, 
            updated_at
        )
    VALUES
        (%s::uuid, %s, %s, %s, %s, NOW())
""").format(table=sql.Identifier(*TRAINING_FEATURE_TABLE))
