#!/usr/bin/env python
"""
Phase 1: Ingest CAS Knowledge

Reads workspace/scratch/pdf_help_ingest/pages.jsonl (pre-extracted PDF pages),
chunks them into 300-500 token segments at section boundaries,
embeds using all-MiniLM-L6-v2,
and stores FAISS index + metadata.

Usage:
    python tools/cli/ingest_cas_knowledge.py
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

import faiss
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from casforge.retrieval.embedding import load_embedding_model
from casforge.shared.paths import CAS_KNOWLEDGE_INDEX_DIR, CAS_KNOWLEDGE_CHUNKS_JSONL, ensure_dir

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_log = logging.getLogger(__name__)

_TARGET_TOKENS_PER_CHUNK = 400
_MIN_CHUNK_TOKENS = 100
_MAX_CHUNK_TOKENS = 500


def _approx_token_count(text: str) -> int:
    """Rough token estimate: 1 token ≈ 4 characters."""
    return max(1, len(text) // 4)


def _split_text_into_chunks(text: str, max_tokens: int = _TARGET_TOKENS_PER_CHUNK) -> list[str]:
    """
    Split text into chunks targeting max_tokens.
    Tries to break at sentence or line boundaries to preserve context.
    """
    if _approx_token_count(text) <= max_tokens:
        return [text]

    chunks = []
    current_chunk = ""
    sentences = text.replace("\n\n", "\n").split(". ")

    for i, sent in enumerate(sentences):
        sent = sent + ("." if i < len(sentences) - 1 else "")
        test_chunk = current_chunk + sent

        if _approx_token_count(test_chunk) > max_tokens:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sent
        else:
            current_chunk = test_chunk

    if current_chunk:
        chunks.append(current_chunk.strip())

    # Filter tiny chunks
    return [c for c in chunks if _approx_token_count(c) >= _MIN_CHUNK_TOKENS]


def _ingest_pages(
    jsonl_path: Path,
    output_index_dir: Path,
    embedding_model: Any,
) -> None:
    """Read JSONL, chunk, embed, and build FAISS index."""

    if not jsonl_path.exists():
        _log.error("Input JSONL not found: %s", jsonl_path)
        return

    _log.info("Reading pages from %s", jsonl_path)
    chunks_data: list[dict[str, Any]] = []
    embeddings: list[np.ndarray] = []
    chunk_counter = 0

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                page = json.loads(line)
            except json.JSONDecodeError as exc:
                _log.warning("Skipping invalid JSON at line %d: %s", line_num, exc)
                continue

            section_title = page.get("section_title", "")
            page_number = page.get("page_number", 0)
            page_text = page.get("text", "").strip()

            if not page_text:
                _log.debug("Skipping empty page %d", page_number)
                continue

            # Try to extract stage/screen hints from section title
            stage_hint = ""
            screen_hint = ""
            if section_title:
                parts = section_title.split("—")
                if len(parts) >= 1:
                    stage_hint = parts[0].strip()
                if len(parts) >= 2:
                    screen_hint = parts[1].strip()

            # Chunk the page
            sub_chunks = _split_text_into_chunks(page_text, _TARGET_TOKENS_PER_CHUNK)

            for sub_idx, chunk_text in enumerate(sub_chunks):
                chunk_counter += 1
                chunk_id = f"cas_chunk_{chunk_counter:06d}"

                # Embed
                try:
                    emb = embedding_model.encode([chunk_text], convert_to_numpy=True).astype("float32")[0]
                    embeddings.append(emb)
                except Exception as exc:
                    _log.error("Failed to embed chunk %s: %s", chunk_id, exc)
                    continue

                # Metadata
                chunks_data.append({
                    "chunk_id": chunk_id,
                    "section_title": section_title,
                    "stage_hint": stage_hint,
                    "screen_hint": screen_hint,
                    "text": chunk_text,
                    "page_range": str(page_number),
                })

    if not embeddings:
        _log.error("No chunks were successfully embedded")
        return

    _log.info("Chunked %d pages into %d segments", line_num, len(embeddings))

    # Build FAISS index
    embedding_dim = embeddings[0].shape[0]
    embeddings_array = np.vstack(embeddings)

    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings_array)

    # Save
    ensure_dir(output_index_dir)
    index_path = output_index_dir / "cas_knowledge.faiss"
    metadata_path = output_index_dir / "metadata.jsonl"

    faiss.write_index(index, str(index_path))
    _log.info("Saved FAISS index to %s", index_path)

    with open(metadata_path, "w", encoding="utf-8") as f:
        for chunk in chunks_data:
            f.write(json.dumps(chunk) + "\n")
    _log.info("Saved metadata to %s", metadata_path)


def main() -> None:
    """Entry point."""
    ensure_dir(CAS_KNOWLEDGE_INDEX_DIR)

    _log.info("Loading embedding model...")
    embedding_model = load_embedding_model()

    _log.info("Ingesting CAS knowledge from %s", CAS_KNOWLEDGE_CHUNKS_JSONL)
    _ingest_pages(CAS_KNOWLEDGE_CHUNKS_JSONL, CAS_KNOWLEDGE_INDEX_DIR, embedding_model)

    _log.info("✓ CAS knowledge ingestion complete")


if __name__ == "__main__":
    main()
