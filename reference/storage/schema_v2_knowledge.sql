-- Phase 1: CAS Domain Knowledge Index Schema
-- Stores chunked segments of the CAS manual with embeddings metadata

CREATE TABLE IF NOT EXISTS cas_knowledge_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id TEXT UNIQUE NOT NULL,
    section_title TEXT,
    stage_hint TEXT,
    screen_hint TEXT,
    page_range TEXT,
    text TEXT NOT NULL,
    embedding_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_chunk_id CHECK (chunk_id ~ '^cas_chunk_\d+$')
);

CREATE INDEX IF NOT EXISTS idx_cas_knowledge_stage_hint ON cas_knowledge_chunks(stage_hint);
CREATE INDEX IF NOT EXISTS idx_cas_knowledge_screen_hint ON cas_knowledge_chunks(screen_hint);
CREATE INDEX IF NOT EXISTS idx_cas_knowledge_embedding_id ON cas_knowledge_chunks(embedding_id);
