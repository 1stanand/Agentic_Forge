"""Build CAS knowledge FAISS index from PDF documents with structure extraction."""
import logging
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import faiss
import pdfplumber
from sentence_transformers import SentenceTransformer

from forge.core.config import get_settings
from forge.core.db import get_conn, get_cursor, release_conn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-7s  %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


def _extract_pdf_structure(pdf_path: Path) -> dict:
    """Extract PDF section structure using font sizes."""
    structure = {}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Calculate average font size to detect headings
            all_sizes = []
            for page in pdf.pages:
                for char in page.chars:
                    if char.get("size"):
                        all_sizes.append(char["size"])

            if not all_sizes:
                return structure

            avg_size = np.mean(all_sizes)
            heading_threshold = avg_size + 1.0  # Headings are noticeably larger

            # Extract headings and group content
            for page_num, page in enumerate(pdf.pages, 1):
                structure[page_num] = {
                    "headings": [],
                    "content_by_heading": {}
                }

                # Extract text lines with font info
                headings_on_page = []
                for text_obj in page.chars:
                    if text_obj.get("size", 0) > heading_threshold:
                        # Likely a heading
                        text = text_obj.get("text", "").strip()
                        if text and len(text) > 1:
                            headings_on_page.append({
                                "text": text,
                                "size": text_obj.get("size")
                            })

                # Use extracted headings, or extract from text if no font info
                if headings_on_page:
                    for heading in headings_on_page:
                        structure[page_num]["headings"].append(heading["text"])
                        structure[page_num]["content_by_heading"][heading["text"]] = ""
                else:
                    # Fallback: look for section separators in text
                    text = page.extract_text() or ""
                    lines = text.split("\n")
                    for line in lines:
                        line_stripped = line.strip()
                        if line_stripped and len(line_stripped) > 3 and line_stripped.isupper():
                            structure[page_num]["headings"].append(line_stripped)
                            structure[page_num]["content_by_heading"][line_stripped] = ""

    except Exception as e:
        logger.warning(f"Could not extract PDF structure from {pdf_path}: {e}")

    return structure


def _infer_stage_hint(section_title: str, chunk_text: str) -> Optional[str]:
    """Infer stage hint from section title and content."""
    if not section_title:
        return None

    section_lower = section_title.lower()
    text_lower = chunk_text.lower()

    # Stage detection patterns
    stage_patterns = {
        "KYC": ["kyc", "know your customer"],
        "Credit Approval": ["credit approval", "credit decision", "credit committee"],
        "Underwriting": ["underwriting", "underwrite", "risk assessment"],
        "Documentation": ["documentation", "document", "docs"],
        "Disbursement": ["disburse", "disbursement", "fund transfer"],
        "Post Disbursal": ["post disbursal", "post-disbursal", "after disbursal"],
    }

    for stage, keywords in stage_patterns.items():
        for keyword in keywords:
            if keyword in section_lower or keyword in text_lower:
                return stage

    return None


def _infer_screen_hint(section_title: str, chunk_text: str) -> Optional[str]:
    """Infer screen hint from section title and content."""
    if not section_title:
        return None

    section_lower = section_title.lower()
    text_lower = chunk_text.lower()

    # Screen detection patterns
    screen_patterns = {
        "Applicant Information": ["applicant", "personal information", "profile"],
        "Collateral": ["collateral", "security", "pledge"],
        "Guarantor": ["guarantor", "co-applicant", "guaranty"],
        "Recommendation": ["recommendation", "proposal", "suggestion"],
        "Approval": ["approval", "approved", "approve"],
        "Application Grid": ["grid", "list", "application list", "applications"],
    }

    for screen, keywords in screen_patterns.items():
        for keyword in keywords:
            if keyword in section_lower or keyword in text_lower:
                return screen

    return None


def extract_pdf_chunks(pdf_path: Path, chunk_size: int = 400) -> list:
    """Extract text chunks from PDF with proper structure detection."""
    chunks = []
    try:
        # Get PDF structure first
        structure = _extract_pdf_structure(pdf_path)

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                if not text.strip():
                    continue

                # Get section info for this page
                page_structure = structure.get(page_num, {})
                current_section = None
                if page_structure.get("headings"):
                    current_section = page_structure["headings"][0]

                # Infer stage and screen hints from section/text
                stage_hint = _infer_stage_hint(current_section or "", text)
                screen_hint = _infer_screen_hint(current_section or "", text)

                # Create chunks
                words = text.split()
                for chunk_idx, i in enumerate(range(0, len(words), chunk_size)):
                    chunk_words = words[i : i + chunk_size]
                    if not chunk_words:
                        continue

                    chunk_text = " ".join(chunk_words)
                    chunk_id = f"{pdf_path.stem}_p{page_num}_c{chunk_idx}"

                    chunks.append(
                        {
                            "chunk_id": chunk_id,
                            "doc_path": str(pdf_path),
                            "section_title": current_section or f"Page {page_num}",
                            "text": chunk_text,
                            "page_range": str(page_num),
                            "stage_hint": stage_hint,
                            "screen_hint": screen_hint,
                            "token_count": len(chunk_words),
                        }
                    )
    except Exception as e:
        logger.error(f"Error extracting {pdf_path}: {e}")

    return chunks


def build_knowledge():
    """Main function to build CAS knowledge index."""
    settings = get_settings()
    cas_docs_path = Path(settings.cas_docs_path)

    if not cas_docs_path.exists():
        logger.warning(f"CAS_DOCS_PATH not found: {cas_docs_path}")
        return

    # Find all PDFs
    pdf_files = list(cas_docs_path.glob("**/*.pdf"))
    if not pdf_files:
        logger.info(f"No PDF files found in {cas_docs_path}")
        return

    logger.info(f"Found {len(pdf_files)} PDF files")

    # Extract chunks from all PDFs
    all_chunks = []
    for pdf_path in pdf_files:
        logger.info(f"Extracting chunks from {pdf_path.name}...")
        chunks = extract_pdf_chunks(pdf_path)
        all_chunks.extend(chunks)
        logger.info(f"  Extracted {len(chunks)} chunks")

    if not all_chunks:
        logger.warning("No chunks extracted from PDFs")
        return

    logger.info(f"Total chunks: {len(all_chunks)}")

    # Log hints population
    chunks_with_stage = sum(1 for c in all_chunks if c.get("stage_hint"))
    chunks_with_screen = sum(1 for c in all_chunks if c.get("screen_hint"))
    logger.info(f"Stage hints populated: {chunks_with_stage}/{len(all_chunks)} ({100*chunks_with_stage/len(all_chunks):.1f}%)")
    logger.info(f"Screen hints populated: {chunks_with_screen}/{len(all_chunks)} ({100*chunks_with_screen/len(all_chunks):.1f}%)")

    # Load embedding model
    logger.info(f"Loading embedding model from {settings.embedding_model}")
    model = SentenceTransformer(str(settings.embedding_model))

    # Embed chunks
    logger.info(f"Embedding {len(all_chunks)} chunks...")
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=256)
    embeddings = embeddings.astype(np.float32)

    # Build IndexFlatL2 (for distance-based retrieval)
    logger.info("Building FAISS index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Save index
    faiss_dir = Path(settings.faiss_index_dir)
    faiss_dir.mkdir(parents=True, exist_ok=True)
    knowledge_path = faiss_dir / "cas_knowledge.faiss"
    faiss.write_index(index, str(knowledge_path))
    logger.info(f"Saved knowledge index to {knowledge_path}")

    # Store chunk metadata in database
    logger.info("Storing chunk metadata in database...")
    conn = get_conn()
    try:
        with get_cursor(conn) as cur:
            # Clear existing chunks
            cur.execute("DELETE FROM doc_chunks")

            # Insert new chunks with FAISS position
            for faiss_pos, chunk in enumerate(all_chunks):
                cur.execute(
                    """
                    INSERT INTO doc_chunks
                    (chunk_id, doc_path, section_title, stage_hint, screen_hint, text, page_range, token_count, faiss_pos)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        chunk["chunk_id"],
                        chunk["doc_path"],
                        chunk["section_title"],
                        chunk["stage_hint"],
                        chunk["screen_hint"],
                        chunk["text"],
                        chunk["page_range"],
                        chunk["token_count"],
                        faiss_pos,
                    ),
                )
        conn.commit()
        logger.info(f"Stored {len(all_chunks)} chunks in database")
    finally:
        release_conn(conn)

    logger.info("Knowledge index build complete")


if __name__ == "__main__":
    build_knowledge()
