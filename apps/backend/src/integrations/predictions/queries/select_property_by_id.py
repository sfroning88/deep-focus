from psycopg2 import sql
from focus_python import PROPERTY_TABLE

QUERY = sql.SQL("""
    SELECT id::text AS id,
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
""").format(table=sql.Identifier(*PROPERTY_TABLE))
