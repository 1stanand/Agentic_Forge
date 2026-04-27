from forge.core.db import get_conn, get_cursor, release_conn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conn = get_conn()
try:
    with get_cursor(conn) as cur:
        logger.info('Dropping old unique_steps view and indices...')
        # Drop indices first, then view
        cur.execute('DROP INDEX IF EXISTS idx_unique_steps_hash CASCADE')
        cur.execute('DROP INDEX IF EXISTS idx_unique_steps_text CASCADE')
        cur.execute('DROP INDEX IF EXISTS idx_unique_steps_trgm CASCADE')
        cur.execute('DROP INDEX IF EXISTS idx_unique_steps_fts CASCADE')
        cur.execute('DROP MATERIALIZED VIEW IF EXISTS unique_steps CASCADE')
        conn.commit()
        logger.info('Dropped')

        logger.info('Creating new unique_steps view with correct definition...')
        create_sql = """
        CREATE MATERIALIZED VIEW unique_steps AS
        SELECT
            md5(s.step_text || '|' || s.step_keyword) AS step_hash,
            s.step_text,
            s.step_keyword,
            min(s.screen_context) AS screen_context,
            min(s.stage_hint) AS stage_hint,
            count(*) AS usage_count,
            array_agg(DISTINCT f.file_name) AS source_files,
            array_agg(DISTINCT f.folder_path) AS source_folders
        FROM steps s
        JOIN scenarios sc ON s.scenario_id = sc.id
        JOIN features f ON s.feature_id = f.id
        WHERE s.is_background = false
        GROUP BY s.step_text, s.step_keyword
        """
        cur.execute(create_sql)
        conn.commit()
        logger.info('View created')

        logger.info('Creating indices (non-unique)...')
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
