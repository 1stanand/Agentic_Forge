from forge.core.db import get_conn, get_cursor, release_conn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conn = get_conn()
try:
    with get_cursor(conn) as cur:
        logger.info('Attempting to REFRESH MATERIALIZED VIEW unique_steps...')
        try:
            cur.execute('REFRESH MATERIALIZED VIEW unique_steps')
            conn.commit()
            logger.info('REFRESH successful')
        except Exception as e:
            logger.error(f'REFRESH failed: {e}')
            conn.rollback()

            # Check the view definition
            logger.info('Checking materialized view definition...')
            cur.execute("""
                SELECT definition
                FROM pg_matviews
                WHERE matviewname = 'unique_steps'
            """)
            result = cur.fetchone()
            if result:
                logger.info(f'View definition: {result[0][:200]}...')

            # Try dropping and recreating
            logger.info('Attempting to DROP and RECREATE materialized view...')
            cur.execute('DROP MATERIALIZED VIEW IF EXISTS unique_steps CASCADE')
            conn.commit()

            create_sql = """
            CREATE MATERIALIZED VIEW unique_steps AS
            SELECT
                md5(step_text || '|' || step_keyword) AS step_hash,
                step_text,
                step_keyword,
                MIN(screen_context) AS screen_context,
                MIN(stage_hint) AS stage_hint,
                COUNT(*) AS usage_count,
                array_agg(DISTINCT f.file_name) AS source_files,
                array_agg(DISTINCT f.folder_path) AS source_folders
            FROM steps s
            JOIN scenarios sc ON s.scenario_id = sc.id
            JOIN features f ON s.feature_id = f.id
            WHERE s.is_background = FALSE
            GROUP BY s.step_text, s.step_keyword
            """

            cur.execute(create_sql)
            conn.commit()
            logger.info('Materialized view recreated')

            # Create indices
            cur.execute('CREATE INDEX idx_unique_steps_hash ON unique_steps(step_hash)')
            cur.execute('CREATE INDEX idx_unique_steps_text ON unique_steps(step_text)')
            cur.execute('CREATE INDEX idx_unique_steps_trgm ON unique_steps USING gin(step_text gin_trgm_ops)')
            cur.execute('CREATE INDEX idx_unique_steps_fts ON unique_steps USING gin(to_tsvector(\'english\', step_text))')
            conn.commit()
            logger.info('Indices created')

        # Verify
        cur.execute('SELECT count(*) as cnt FROM unique_steps')
        result = cur.fetchone()
        unique_count = result['cnt'] if result else 0
        logger.info(f'unique_steps now contains {unique_count} rows')

finally:
    release_conn(conn)
