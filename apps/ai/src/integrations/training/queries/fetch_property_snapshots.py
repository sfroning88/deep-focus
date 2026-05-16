from psycopg2 import sql
from focus_python import PROPERTY_SNAPSHOT_TABLE

QUERY = sql.SQL("""
    SELECT
        property_id::text AS property_id,
        reported_at,
        occupancy,
        total_revenues,
        controllable_expenses,
        controllable_prd,
        function
    FROM {table}
""").format(table=sql.Identifier(*PROPERTY_SNAPSHOT_TABLE))
