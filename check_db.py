from forge.core.db import get_conn, get_cursor, release_conn

conn = get_conn()
try:
    with get_cursor(conn) as cur:
        cur.execute('SELECT count(*) as cnt FROM unique_steps')
        result = cur.fetchone()
        unique_count = result['cnt'] if result else 0
        print(f'Rows in unique_steps view: {unique_count}')

        cur.execute('SELECT count(*) as cnt FROM steps')
        result = cur.fetchone()
        steps_count = result['cnt'] if result else 0
        print(f'Rows in steps table: {steps_count}')

        if unique_count == 0 and steps_count > 0:
            cur.execute('SELECT count(*) as cnt FROM steps WHERE is_background = FALSE')
            result = cur.fetchone()
            non_bg = result['cnt'] if result else 0
            print(f'Non-background steps: {non_bg}')

            # Try to check if the view exists
            cur.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables
                    WHERE table_name = 'unique_steps'
                    AND table_type = 'MATERIALIZED VIEW'
                )
            """)
            exists = cur.fetchone()[0]
            print(f'unique_steps materialized view exists: {exists}')
finally:
    release_conn(conn)
