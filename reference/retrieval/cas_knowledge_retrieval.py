"""
Phase 1: CAS Domain Knowledge Retrieval

Retrieves chunks from the CAS manual via FAISS vector similarity.
Separate index from the repo steps index — different domains, different embedding sources.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

import faiss
import numpy as np

from casforge.shared.paths import CAS_KNOWLEDGE_INDEX_DIR, CAS_KNOWLEDGE_CHUNKS_JSONL
from casforge.retrieval.embedding import load_embedding_model

_log = logging.getLogger(__name__)

# Lazy-loaded cache
_faiss_index: Optional[Any] = None
_chunk_metadata: Optional[list[dict[str, Any]]] = None


def _load_cas_index() -> tuple[Any, list[dict[str, Any]]]:
    """Load FAISS index and metadata for CAS knowledge chunks."""
    global _faiss_index, _chunk_metadata

    if _faiss_index is not None and _chunk_metadata is not None:
        return _faiss_index, _chunk_metadata

    index_path = CAS_KNOWLEDGE_INDEX_DIR / "cas_knowledge.faiss"
    metadata_path = CAS_KNOWLEDGE_INDEX_DIR / "metadata.jsonl"

    if not index_path.exists() or not metadata_path.exists():
        _log.warning("CAS knowledge index not found at %s. Run ingest_cas_knowledge.py first.", CAS_KNOWLEDGE_INDEX_DIR)
        return None, []

    try:
        _faiss_index = faiss.read_index(str(index_path))
        _chunk_metadata = []
        with open(metadata_path, "r", encoding="utf-8") as f:
            for line in f:
                _chunk_metadata.append(json.loads(line))
        _log.debug("Loaded CAS knowledge index with %d chunks", len(_chunk_metadata))
        return _faiss_index, _chunk_metadata
    except Exception as exc:
        _log.error("Failed to load CAS knowledge index: %s", exc)
        return None, []


def retrieve_cas_knowledge(
    query: str,
    top_k: int = 5,
    stage_hint: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Retrieve top-k CAS manual chunks relevant to the given query.

    Args:
        query: Text query to embed and search
        top_k: Number of results to return
        stage_hint: Optional stage hint to boost matching chunks

    Returns:
        List of chunk dicts with keys: chunk_id, section_title, stage_hint, screen_hint, text, page_range
    """
    index, metadata = _load_cas_index()

    if index is None or not metadata:
        _log.debug("CAS knowledge index not available, returning empty results")
        return []

    if not query or not query.strip():
        return []

    try:
        # Embed the query using the same model as the index
        embed_model = load_embedding_model()
        query_embedding = embed_model.encode([query.strip()], convert_to_numpy=True).astype("float32")

        # Search index
        distances, indices = index.search(query_embedding, min(top_k * 2, len(metadata)))

        results = []
        for idx in indices[0]:
            if idx < 0 or idx >= len(metadata):
                continue

            chunk = metadata[idx].copy()

            # Boost if stage matches hint
            if stage_hint and chunk.get("stage_hint", "").lower() == stage_hint.lower():
                chunk["_boost"] = True

            results.append(chunk)

        # Sort by boost, then by original order
        results.sort(key=lambda x: (not x.pop("_boost", False), results.index(x)))
        return results[:top_k]

    except Exception as exc:
        _log.error("CAS knowledge retrieval failed for query '%s': %s", query, exc)
        return []


def reset_cache() -> None:
    """Clear the in-memory cache (for testing)."""
    global _faiss_index, _chunk_metadata
    _faiss_index = None
    _chunk_metadata = None
