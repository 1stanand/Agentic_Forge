import argparse
import logging
import sys

from forge.core.db import get_conn, get_cursor, release_conn
from forge.core.config import get_settings

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    display_name    VARCHAR(200),
    is_admin        BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    jira_pat        TEXT,
    theme_pref      VARCHAR(10) DEFAULT 'dark',
    created_at      TIMESTAMP DEFAULT NOW(),
    last_login      TIMESTAMP
);

CREATE TABLE user_settings (
    user_id         INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    jira_url        VARCHAR(500),
    jira_pat        TEXT,
    ollama_url      VARCHAR(500),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_sessions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(200),
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role         VARCHAR(20) NOT NULL,
    content      TEXT NOT NULL,
    context_type VARCHAR(20),
    created_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE generation_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         INTEGER REFERENCES users(id),
    status          VARCHAR(20) DEFAULT 'pending',
    jira_story_id   VARCHAR(50),
    flow_type       VARCHAR(20),
    module          VARCHAR(20) DEFAULT 'cas',
    feature_file    TEXT,
    gap_report      JSONB,
    confidence_score FLOAT,
    error_message   TEXT,
    current_agent   INTEGER DEFAULT 0,
    elapsed_seconds INTEGER DEFAULT 0,
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE features (
    id              SERIAL PRIMARY KEY,
    file_path       TEXT UNIQUE NOT NULL,
    file_name       TEXT NOT NULL,
    folder_path     TEXT,
    flow_type       VARCHAR(20),
    file_tags       TEXT[],
    file_dicts      JSONB,
    file_annotations TEXT[],
    scenario_count  INTEGER DEFAULT 0,
    lobs_present    TEXT[],
    stages_present  TEXT[],
    story_ids       TEXT[],
    mtime           FLOAT,
    has_conflict    BOOLEAN DEFAULT FALSE,
    parse_error     TEXT,
    indexed_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE scenarios (
    id                  SERIAL PRIMARY KEY,
    feature_id          INTEGER REFERENCES features(id) ON DELETE CASCADE,
    title               TEXT NOT NULL,
    scenario_type       VARCHAR(30),
    scenario_tags       TEXT[],
    scenario_dicts      JSONB,
    scenario_annotations TEXT[],
    logical_id          TEXT,
    step_count          INTEGER DEFAULT 0,
    position            INTEGER,
    has_examples        BOOLEAN DEFAULT FALSE
);

CREATE TABLE steps (
    id              SERIAL PRIMARY KEY,
    scenario_id     INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
    feature_id      INTEGER REFERENCES features(id) ON DELETE CASCADE,
    step_keyword    VARCHAR(20),
    step_text       TEXT NOT NULL,
    step_position   INTEGER,
    screen_context  TEXT,
    stage_hint      TEXT,
    is_background   BOOLEAN DEFAULT FALSE,
    has_docstring   BOOLEAN DEFAULT FALSE,
    docstring_text  TEXT
);

CREATE TABLE example_blocks (
    id              SERIAL PRIMARY KEY,
    scenario_id     INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
    block_position  INTEGER,
    headers         TEXT[],
    rows            JSONB,
    block_dicts     JSONB,
    block_tags      TEXT[]
);

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
GROUP BY s.step_text, s.step_keyword;

CREATE INDEX idx_unique_steps_hash ON unique_steps(step_hash);
CREATE INDEX idx_unique_steps_text ON unique_steps(step_text);
CREATE INDEX idx_steps_screen ON steps(screen_context);
CREATE INDEX idx_steps_text_trgm ON steps USING gin(step_text gin_trgm_ops);
CREATE INDEX idx_unique_steps_trgm ON unique_steps USING gin(step_text gin_trgm_ops);
CREATE INDEX idx_steps_fts ON steps USING gin(to_tsvector('english', step_text));
CREATE INDEX idx_unique_steps_fts ON unique_steps USING gin(to_tsvector('english', step_text));
CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_jobs_user ON generation_jobs(user_id);
CREATE INDEX idx_jobs_status ON generation_jobs(status);
CREATE INDEX idx_jobs_updated_at ON generation_jobs(updated_at);

CREATE TABLE doc_chunks (
    id              SERIAL PRIMARY KEY,
    chunk_id        TEXT UNIQUE NOT NULL,
    doc_path        TEXT,
    section_title   TEXT,
    stage_hint      TEXT,
    screen_hint     TEXT,
    text            TEXT NOT NULL,
    page_range      TEXT,
    token_count     INTEGER,
    faiss_pos       INTEGER
);

CREATE TABLE rag_cache (
    id          SERIAL PRIMARY KEY,
    cache_key   TEXT UNIQUE NOT NULL,
    summary     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    hit_count   INTEGER DEFAULT 0
);

CREATE INDEX idx_doc_chunks_stage ON doc_chunks(stage_hint);
CREATE INDEX idx_doc_chunks_screen ON doc_chunks(screen_hint);
"""


def setup_db():
    try:
        conn = get_conn()
        with get_cursor(conn) as cursor:
            cursor.execute(SCHEMA_SQL)
        logger.info("Database schema created successfully")
        release_conn(conn)
        return True
    except Exception as e:
        logger.error(f"Failed to create schema: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Setup Forge database')
    parser.add_argument('--fresh', action='store_true', help='Drop all tables and recreate')
    args = parser.parse_args()

    settings = get_settings()
    logger.info(f"Setting up database: {settings.db_host}:{settings.db_port}/{settings.db_name}")

    if args.fresh:
        logger.info("Fresh rebuild: dropping all tables...")
        conn = get_conn()
        try:
            with get_cursor(conn) as cursor:
                cursor.execute("""
                    DROP MATERIALIZED VIEW IF EXISTS unique_steps CASCADE;
                    DROP TABLE IF EXISTS rag_cache CASCADE;
                    DROP TABLE IF EXISTS doc_chunks CASCADE;
                    DROP TABLE IF EXISTS example_blocks CASCADE;
                    DROP TABLE IF EXISTS steps CASCADE;
                    DROP TABLE IF EXISTS scenarios CASCADE;
                    DROP TABLE IF EXISTS features CASCADE;
                    DROP TABLE IF EXISTS generation_jobs CASCADE;
                    DROP TABLE IF EXISTS chat_messages CASCADE;
                    DROP TABLE IF EXISTS chat_sessions CASCADE;
                    DROP TABLE IF EXISTS user_settings CASCADE;
                    DROP TABLE IF EXISTS users CASCADE;
                """)
            logger.info("All tables dropped")
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
        finally:
            release_conn(conn)

    if setup_db():
        logger.info("Database ready")
        sys.exit(0)
    else:
        logger.error("Database setup failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
