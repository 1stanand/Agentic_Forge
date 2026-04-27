import logging
from sentence_transformers import CrossEncoder

from forge.core.config import get_settings
from forge.core.db import get_conn, get_cursor, release_conn
from forge.infrastructure.embedder import load_index, search_index, load_embedding_model
from forge.infrastructure.query_expander import normalise_query_text, expand_for_vector, expand_for_fts
from forge.infrastructure.order_json_reader import detect_stage
from forge.infrastructure.graph_rag import validate_step

logger = logging.getLogger(__name__)

_cross_encoder = None


def get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        settings = get_settings()
        try:
            _cross_encoder = CrossEncoder(str(settings.cross_encoder_model), max_length=512)
            logger.info("Cross-encoder loaded")
        except Exception as e:
            logger.warning(f"Could not load cross-encoder: {e}")
            _cross_encoder = False
    return _cross_encoder if _cross_encoder else None


def retrieve(action_text: str, top_k: int = 20, screen_filter: str = None, stage_hint: str = None, retry_count: int = 0) -> list:
    """Full step retrieval stack."""
    try:
        index, step_hashes = load_index()
    except Exception as e:
        logger.error(f"Could not load FAISS index: {e}")
        return []

    # Prepare queries
    normalized = normalise_query_text(action_text)
    vector_query = expand_for_vector(normalized)
    fts_query = expand_for_fts(normalized)

    # FAISS search
    vector_results = search_index(index, step_hashes, vector_query, top_k * 3)

    # FTS search
    conn = get_conn()
    try:
        with get_cursor(conn) as cur:
            cur.execute(f"""
                SELECT step_hash, step_text FROM unique_steps
                WHERE to_tsvector('english', step_text) @@ plainto_tsquery('english', %s)
                LIMIT {top_k * 3}
            """, (fts_query,))
            fts_results = [(row['step_hash'], 0.5) for row in cur.fetchall()]

            # Trigram search
            cur.execute(f"""
                SELECT step_hash, step_text, similarity(step_text, %s) AS sim
                FROM unique_steps
                WHERE similarity(step_text, %s) > 0.2
                ORDER BY sim DESC
                LIMIT {top_k * 3}
            """, (normalized, normalized))
            trgm_results = [(row['step_hash'], 1.0 - row['sim']) for row in cur.fetchall()]
    finally:
        release_conn(conn)

    # Merge results with weighting (50/30/20)
    merged = {}
    for step_hash, score in vector_results:
        merged[step_hash] = merged.get(step_hash, 0) + score * 0.5

    for step_hash, score in fts_results:
        merged[step_hash] = merged.get(step_hash, 0) + (1.0 - score) * 0.3 if score < 1.0 else 0.3

    for step_hash, score in trgm_results:
        merged[step_hash] = merged.get(step_hash, 0) + (1.0 - score) * 0.2 if score < 1.0 else 0.2

    # Sort by merged score
    sorted_results = sorted(merged.items(), key=lambda x: -x[1])[:top_k]

    # Fetch full context and apply cross-encoder
    conn = get_conn()
    try:
        final_results = []
        for step_hash, merged_score in sorted_results:
            with get_cursor(conn) as cur:
                cur.execute("SELECT step_text, step_keyword, screen_context FROM unique_steps WHERE step_hash = %s", (step_hash,))
                row = cur.fetchone()
                if row:
                    step_data = {
                        "step_hash": step_hash,
                        "step_text": row["step_text"],
                        "step_keyword": row["step_keyword"],
                        "screen_context": row["screen_context"],
                        "merged_score": merged_score,
                        "ce_score": None,
                        "marker": None,
                    }

                    # Cross-encoder reranking
                    ce = get_cross_encoder()
                    if ce:
                        try:
                            ce_score = ce.predict([(action_text, row["step_text"])])[0]
                            step_data["ce_score"] = float(ce_score)
                        except Exception as e:
                            logger.warning(f"Cross-encoder error: {e}")
                            step_data["ce_score"] = 0.5

                    # Assign marker based on ce_score
                    if step_data["ce_score"] is not None:
                        if step_data["ce_score"] >= 0.7:
                            step_data["marker"] = None
                        elif step_data["ce_score"] >= 0.3:
                            step_data["marker"] = "[LOW_MATCH]"
                        else:
                            step_data["marker"] = "[NEW_STEP_NOT_IN_REPO]"
                    else:
                        step_data["marker"] = "[NEW_STEP_NOT_IN_REPO]"

                    # GraphRAG validation
                    role_gap = validate_step(row["step_text"], stage_hint, screen_filter)
                    if role_gap:
                        step_data["marker"] = role_gap

                    final_results.append(step_data)

        # Self-RAG gate
        if final_results and final_results[0].get("ce_score", 0) < get_settings().low_match_threshold and retry_count == 0:
            logger.info("Self-RAG: top match below threshold, retrying with expanded query...")
            expanded = expand_for_vector(action_text) + " " + action_text
            return retrieve(expanded, top_k, screen_filter, stage_hint, retry_count=1)

        return final_results

    finally:
        release_conn(conn)


def get_settings():
    from forge.core.config import get_settings
    return get_settings()
