import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer
import logging

from forge.core.config import get_settings

logger = logging.getLogger(__name__)

_model = None


def load_embedding_model():
    global _model
    if _model is None:
        settings = get_settings()
        logger.info(f"Loading embedding model from {settings.embedding_model}")
        _model = SentenceTransformer(str(settings.embedding_model))
    return _model


def build_index(step_rows: list) -> None:
    """Build FAISS index from step rows (must have step_hash and step_text)."""
    if not step_rows:
        logger.warning("No steps to index")
        return

    settings = get_settings()
    model = load_embedding_model()

    logger.info(f"Embedding {len(step_rows)} steps...")
    texts = [row["step_text"] for row in step_rows]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=256)

    # Normalize for cosine similarity
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    # Build IndexFlatIP (inner product on unit vectors = cosine)
    logger.info(f"Building FAISS index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype(np.float32))

    # Save index and step_hash map
    faiss_dir = Path(settings.faiss_index_dir)
    faiss_dir.mkdir(parents=True, exist_ok=True)

    index_path = faiss_dir / "faiss_index.bin"
    map_path = faiss_dir / "step_id_map.npy"

    faiss.write_index(index, str(index_path))
    step_hashes = np.array([row["step_hash"] for row in step_rows], dtype=object)
    np.save(map_path, step_hashes)

    logger.info(f"Saved index to {index_path}")
    logger.info(f"Saved step map to {map_path}")


def load_index() -> tuple:
    """Load FAISS index and step_hash map from disk."""
    settings = get_settings()
    faiss_dir = Path(settings.faiss_index_dir)

    index_path = faiss_dir / "faiss_index.bin"
    map_path = faiss_dir / "step_id_map.npy"

    if not index_path.exists():
        raise FileNotFoundError(f"FAISS index not found: {index_path}")
    if not map_path.exists():
        raise FileNotFoundError(f"Step map not found: {map_path}")

    index = faiss.read_index(str(index_path))
    step_hashes = np.load(map_path, allow_pickle=True)

    logger.info(f"Loaded FAISS index with {index.ntotal} vectors")
    return index, step_hashes


def search_index(index, step_hashes: np.ndarray, query_text: str, top_k: int = 50) -> list:
    """Search FAISS index for similar steps."""
    model = load_embedding_model()
    query_embedding = model.encode([query_text])[0]
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    distances, indices = index.search(np.array([query_embedding], dtype=np.float32), top_k)

    results = []
    for distance, idx in zip(distances[0], indices):
        if idx >= 0 and idx < len(step_hashes):
            results.append((step_hashes[idx], float(distance)))

    return results
