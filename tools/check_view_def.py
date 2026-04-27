from forge.core.db import get_conn, get_cursor, release_conn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conn = get_conn()
try:
    with get_cursor(conn) as cur:
        # Get the view definition
        cur.execute("""
            SELECT definition
            FROM pg_matviews
            WHERE matviewname = 'unique_steps'
        """)
        result = cur.fetchone()
        if result:
            defn = result[0] if isinstance(result, tuple) else result.get('definition')
            print('Current unique_steps view definition:')
            print(defn)
        else:
            print('View not found')
finally:
    release_conn(conn)
