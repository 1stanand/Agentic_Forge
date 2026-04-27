"""Build FAISS step index from unique_steps view."""
import logging
import sys
from pathlib import Path

from forge.core.config import get_settings
from forge.core.db import get_conn, get_cursor, release_conn
from forge.infrastructure.embedder import build_index

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-7s  %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


def main():
    settings = get_settings()

    # Ensure FAISS index directory exists
    faiss_dir = Path(settings.faiss_index_dir)
    faiss_dir.mkdir(parents=True, exist_ok=True)

    conn = get_conn()
    try:
        with get_cursor(conn) as cur:
            logger.info('Loading unique steps from DB...')
            cur.execute(
                'SELECT step_hash, step_text FROM unique_steps ORDER BY step_hash'
            )
            rows = cur.fetchall()
        logger.info(f'Loaded {len(rows)} unique steps')
    finally:
        release_conn(conn)

    if not rows:
        logger.error('No steps found in DB. Run index_repo.py first.')
        sys.exit(1)

    # Convert rows to list of dicts
    rows_list = [
        {'step_hash': r['step_hash'], 'step_text': r['step_text']}
        for r in rows
    ]

    try:
        build_index(rows_list)
        logger.info(f'Index build complete. Files in {faiss_dir}')
    except Exception as e:
        logger.error(f'Index build failed: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
