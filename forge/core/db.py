import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import logging

from forge.core.config import get_settings

logger = logging.getLogger(__name__)

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port
        )
        logger.info(f"PostgreSQL connection pool initialized: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    return _pool


def get_conn():
    """Get a connection from the pool."""
    pool = _get_pool()
    return pool.getconn()


def release_conn(conn):
    """Release a connection back to the pool."""
    pool = _get_pool()
    pool.putconn(conn)


@contextmanager
def get_cursor(conn, dict_cursor=True):
    """Context manager for database cursors with transaction safety."""
    cursor = None
    try:
        if dict_cursor:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()


def run_sql_file(file_path: str):
    """Execute SQL from a file."""
    conn = get_conn()
    try:
        with open(file_path, 'r') as f:
            sql = f.read()
        with get_cursor(conn) as cursor:
            cursor.execute(sql)
        logger.info(f"Executed SQL file: {file_path}")
    finally:
        release_conn(conn)


def test_connection():
    """Test database connectivity."""
    try:
        conn = get_conn()
        with get_cursor(conn) as cursor:
            cursor.execute("SELECT 1")
        release_conn(conn)
        logger.info("Database connection test passed")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
