import logging
import numpy as np

from forge.core.config import get_settings
from forge.core.db import get_conn, get_cursor, release_conn
from forge.infrastructure.embedder import load_index, load_embedding_model
from forge.core.llm import llm_complete, LLMNotLoadedError

logger = logging.getLogger(__name__)

_cas_index = None
_cas_index_type = None


def load_cas_knowledge_index():
    """Load CAS knowledge FAISS index and metadata."""
    global _cas_index
    if _cas_index is not None:
        return _cas_index

    try:
        settings = get_settings()
        from pathlib import Path
        import faiss
        index_path = Path(settings.faiss_index_dir) / "cas_knowledge.faiss"
        if not index_path.exists():
            logger.warning(f"CAS knowledge index not found at {index_path}")
            return None
        _cas_index = faiss.read_index(str(index_path))
        logger.info("CAS knowledge index loaded")
        return _cas_index
    except Exception as e:
        logger.error(f"Could not load CAS knowledge index: {e}")
        return None


def get_context(screen: str = None, stage: str = None, lob: str = None, query: str = None, top_k: int = 5, module: str = "cas") -> str:
    """Retrieve and synthesize knowledge using RAG. Module-scoped to support CAS, LMS, etc."""
    settings = get_settings()

    # Cache check
    cache_key = f"{module}_{screen}_{stage}_{lob}".replace(" ", "_")
    conn = get_conn()
    try:
        with get_cursor(conn) as cur:
            cur.execute("SELECT summary FROM rag_cache WHERE cache_key = %s", (cache_key,))
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE rag_cache SET hit_count = hit_count + 1 WHERE cache_key = %s", (cache_key,))
                conn.commit()
                return row["summary"]
    finally:
        release_conn(conn)

    # Cache miss - fetch and distill
    index = load_cas_knowledge_index()
    if index is None:
        return "CAS knowledge not available"

    try:
        model = load_embedding_model()
        if query:
            query_embedding = model.encode(query)
        else:
            query_embedding = model.encode(f"{screen} {stage} {lob}")

        query_embedding = query_embedding.astype(np.float32)
        distances, indices = index.search(np.array([query_embedding], dtype=np.float32), top_k * 2)

        # Fetch chunk metadata (module-scoped)
        conn = get_conn()
        chunks = []
        try:
            for idx in indices[0]:
                if idx >= 0:
                    with get_cursor(conn) as cur:
                        cur.execute(
                            "SELECT text, stage_hint, screen_hint, lob_hint FROM doc_chunks WHERE faiss_pos = %s AND source_module = %s",
                            (int(idx), module)
                        )
                        row = cur.fetchone()
                        if row:
                            # Optional LOB boost: if lob parameter provided and matches chunk, boost weight
                            text = row["text"]
                            if lob and row.get("lob_hint") and row["lob_hint"].lower() == lob.lower():
                                text = f"[LOB-MATCH] {text}"
                            chunks.append(text)
        finally:
            release_conn(conn)

        if not chunks:
            return "No CAS knowledge found"

        # On-demand distillation with LLM
        context_text = "\n\n".join(chunks[:top_k])
        try:
            summary = llm_complete(
                context_text,
                system=f"""You are a CAS domain expert. Summarize the following CAS documentation
                for a tester working on screen '{screen}' at stage '{stage}' for LOB '{lob}'.
                Be specific. Focus on fields, rules, and conditional behavior.""",
                max_tokens=512
            )
        except LLMNotLoadedError:
            logger.warning("LLM not loaded, returning raw chunks")
            summary = context_text

        # Cache result
        conn = get_conn()
        try:
            with get_cursor(conn) as cur:
                cur.execute(
                    """INSERT INTO rag_cache (cache_key, summary, hit_count)
                    VALUES (%s, %s, 1)
                    ON CONFLICT (cache_key) DO UPDATE SET
                        summary = EXCLUDED.summary,
                        hit_count = rag_cache.hit_count + 1""",
                    (cache_key, summary)
                )
            conn.commit()
        finally:
            release_conn(conn)

        return summary

    except Exception as e:
        logger.error(f"RAG engine error: {e}")
        return f"Error retrieving CAS knowledge: {e}"
