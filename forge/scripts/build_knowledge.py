"""Build knowledge wiki from seed taxonomy + PDFs. Hybrid approach: Python hints + LLM for ambiguous chunks."""
import argparse
import logging
import sys
import re
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from collections import defaultdict
from slugify import slugify

import numpy as np
import faiss
import pdfplumber
import tomllib
from sentence_transformers import SentenceTransformer

from forge.core.config import get_settings
from forge.core.db import get_conn, get_cursor, release_conn
from forge.core.llm import llm_complete, LLMNotLoadedError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-7s  %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


class TaxonomyLoader:
    """Load and normalize CAS seed taxonomy from TOML."""

    def __init__(self, module: str):
        self.module = module
        self.taxonomy_dir = Path("data/knowledge") / module / "taxanomy_source"
        self.taxonomy_file = self.taxonomy_dir / f"{module}_bootstrap_taxonomy.toml"
        self.data = None
        self.lobs = {}
        self.stages = {}
        self.screens = {}

    def load(self) -> bool:
        """Load taxonomy from TOML."""
        if not self.taxonomy_file.exists():
            logger.error(f"Taxonomy file not found: {self.taxonomy_file}")
            return False

        try:
            with open(self.taxonomy_file, 'rb') as f:
                self.data = tomllib.load(f)
        except Exception as e:
            logger.error(f"Failed to load taxonomy: {e}")
            return False

        # Build LOB map: canonical names, codes, aliases -> canonical
        self.lobs['canonical'] = self.data.get('lobs', {}).get('canonical', [])
        self.lobs['codes'] = self.data.get('lobs', {}).get('codes', {})
        self.lobs['aliases'] = self.data.get('lobs', {}).get('aliases', {})

        # Normalize: all variants -> canonical
        self.lobs['all_map'] = {}
        for canonical in self.lobs['canonical']:
            self.lobs['all_map'][canonical.lower()] = canonical
        for code, canonical in self.lobs['codes'].items():
            self.lobs['all_map'][code.lower()] = canonical
        for variant, canonical in self.lobs['aliases'].items():
            self.lobs['all_map'][variant.lower()] = canonical

        # Stages
        self.stages['canonical'] = self.data.get('stages', {}).get('canonical', [])
        self.stages['aliases'] = self.data.get('stages', {}).get('aliases', {})
        self.stages['entries'] = self.data.get('stage', [])  # [[stage]] array

        # Build stage name -> page_range map
        self.stages['page_ranges'] = {}
        for stage_entry in self.stages['entries']:
            name = stage_entry.get('name')
            start = stage_entry.get('page_start')
            end = stage_entry.get('page_end')
            if name and start and end:
                self.stages['page_ranges'][name] = (start, end)

        # Normalize: all variants -> canonical
        self.stages['all_map'] = {}
        for canonical in self.stages['canonical']:
            self.stages['all_map'][canonical.lower()] = canonical
        for alias, canonical in self.stages['aliases'].items():
            self.stages['all_map'][alias.lower()] = canonical

        # Screens
        self.screens['canonical'] = self.data.get('screens', {}).get('canonical', [])
        self.screens['aliases'] = self.data.get('screens', {}).get('aliases', {})

        # Normalize: all variants -> canonical
        self.screens['all_map'] = {}
        for canonical in self.screens['canonical']:
            self.screens['all_map'][canonical.lower()] = canonical
        for alias, canonical in self.screens['aliases'].items():
            self.screens['all_map'][alias.lower()] = canonical

        logger.info(f"[OK] Taxonomy loaded: {len(self.lobs['canonical'])} LOBs, {len(self.stages['canonical'])} stages, {len(self.screens['canonical'])} screens")
        return True


def _extract_pdf_structure(pdf_path: Path) -> dict:
    """Extract PDF section structure using font sizes."""
    structure = {}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_sizes = []
            for page in pdf.pages:
                for char in page.chars:
                    if char.get("size"):
                        all_sizes.append(char["size"])

            if not all_sizes:
                return structure

            avg_size = np.mean(all_sizes)
            heading_threshold = avg_size + 1.0

            for page_num, page in enumerate(pdf.pages, 1):
                structure[page_num] = {"headings": [], "content_by_heading": {}}

                headings_on_page = []
                for text_obj in page.chars:
                    if text_obj.get("size", 0) > heading_threshold:
                        text = text_obj.get("text", "").strip()
                        if text and len(text) > 1:
                            headings_on_page.append({"text": text, "size": text_obj.get("size")})

                if headings_on_page:
                    for heading in headings_on_page:
                        structure[page_num]["headings"].append(heading["text"])
                        structure[page_num]["content_by_heading"][heading["text"]] = ""
                else:
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


def assign_stage_hint(page_num: int, taxonomy: TaxonomyLoader) -> Tuple[Optional[str], float]:
    """Assign stage hint: page range match (deterministic, high confidence)."""
    for stage_entry in taxonomy.stages['entries']:
        start = stage_entry.get('page_start')
        end = stage_entry.get('page_end')
        if start and end and start <= page_num <= end:
            return stage_entry.get('name'), 0.95

    return None, 0.0


def assign_lob_hint(text: str, section_title: str, taxonomy: TaxonomyLoader) -> Tuple[Optional[str], float]:
    """Assign LOB hint: keyword matching with alias expansion."""
    if not text:
        return None, 0.0

    text_lower = text.lower()
    section_lower = (section_title or "").lower()
    combined = f"{text_lower} {section_lower}"

    lob_counts = defaultdict(int)

    # Count hits for each canonical LOB
    for variant, canonical in taxonomy.lobs['all_map'].items():
        # Match whole words or with word boundaries
        pattern = r'\b' + re.escape(variant) + r'\b'
        hits = len(re.findall(pattern, combined, re.IGNORECASE))
        if hits > 0:
            lob_counts[canonical] += hits

    if not lob_counts:
        return None, 0.0

    # Get top LOB
    top_lob = max(lob_counts.items(), key=lambda x: x[1])[0]
    hit_count = lob_counts[top_lob]

    # Confidence: 3+ hits = 0.75, 1-2 hits = 0.4
    if hit_count >= 3:
        confidence = 0.75
    else:
        confidence = 0.4

    return top_lob, confidence


def assign_screen_hint(section_title: str, text: str, taxonomy: TaxonomyLoader) -> Tuple[Optional[str], float]:
    """Assign screen hint: exact match > alias > keyword."""
    if not section_title:
        return None, 0.0

    section_lower = section_title.lower()
    text_lower = (text or "").lower()

    # Direct title match
    if section_lower in taxonomy.screens['all_map']:
        return taxonomy.screens['all_map'][section_lower], 0.9

    # Scan for keywords in title
    for variant, canonical in taxonomy.screens['all_map'].items():
        if variant in section_lower:
            return canonical, 0.85

    # Scan text for screen keywords
    for variant, canonical in taxonomy.screens['all_map'].items():
        pattern = r'\b' + re.escape(variant) + r'\b'
        if re.search(pattern, text_lower, re.IGNORECASE):
            return canonical, 0.5

    return None, 0.0


def classify_chunk_type(text: str, section_title: str, stage_hint: Optional[str], screen_hint: Optional[str]) -> str:
    """Classify chunk type: procedure > screen > stage > concept."""
    text_lower = (text or "").lower()

    if any(kw in text_lower for kw in ["step 1", "step 2", "step 3", "1.", "2.", "3.", "procedure", "how to", "instructions"]):
        return "procedure"

    if any(kw in text_lower for kw in ["field", "mandatory", "optional", "required", "enter the", "select the", "tab", "button"]):
        return "screen"

    if stage_hint and not screen_hint:
        return "stage"

    return "concept"


def extract_pdf_chunks(pdf_path: Path, taxonomy: TaxonomyLoader, chunk_size: int = 400) -> list:
    """Extract chunks with taxonomy-driven hints."""
    chunks = []
    try:
        structure = _extract_pdf_structure(pdf_path)

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                if not text.strip():
                    continue

                page_structure = structure.get(page_num, {})
                current_section = None
                if page_structure.get("headings"):
                    current_section = page_structure["headings"][0]

                # Assign hints using taxonomy
                stage_hint, stage_conf = assign_stage_hint(page_num, taxonomy)
                lob_hint, lob_conf = assign_lob_hint(text, current_section or "", taxonomy)
                screen_hint, screen_conf = assign_screen_hint(current_section or "", text, taxonomy)

                # Chunk type
                chunk_type = classify_chunk_type(text, current_section or "", stage_hint, screen_hint)

                # Average confidence
                confidences = [c for c in [stage_conf, lob_conf, screen_conf] if c > 0.0]
                avg_conf = np.mean(confidences) if confidences else 0.0

                # Create chunks
                words = text.split()
                for chunk_idx, i in enumerate(range(0, len(words), chunk_size)):
                    chunk_words = words[i : i + chunk_size]
                    if not chunk_words:
                        continue

                    chunk_text = " ".join(chunk_words)
                    chunk_id = f"{pdf_path.stem}_p{page_num}_c{chunk_idx}"

                    chunks.append({
                        "chunk_id": chunk_id,
                        "doc_path": str(pdf_path),
                        "section_title": current_section or f"Page {page_num}",
                        "text": chunk_text,
                        "page_range": str(page_num),
                        "stage_hint": stage_hint,
                        "screen_hint": screen_hint,
                        "lob_hint": lob_hint,
                        "chunk_type": chunk_type,
                        "hint_confidence": float(avg_conf),
                        "token_count": len(chunk_words),
                    })
    except Exception as e:
        logger.error(f"Error extracting {pdf_path}: {e}")

    return chunks


def apply_llm_hints(chunks: List[Dict], taxonomy: TaxonomyLoader) -> List[Dict]:
    """For ambiguous chunks (all hints < 0.4), call LLM for classification. Hybrid approach."""
    llm_prompt = """Classify this PDF chunk. Return JSON with stage_hint, lob_hint, screen_hint, chunk_type, confidence.
chunk_type: 'procedure' | 'screen' | 'stage' | 'concept'
confidence: 0.0 to 1.0

Valid values:
stages: {stages}
lobs: {lobs}
screens: {screens}

Chunk:
{chunk_text}

Return JSON only, no explanation."""

    stages_str = ", ".join(taxonomy.stages['canonical'][:10])  # Sample
    lobs_str = ", ".join(taxonomy.lobs['canonical'][:10])
    screens_str = ", ".join(taxonomy.screens['canonical'][:10])

    updated = 0
    for chunk in chunks:
        # Only invoke LLM if all hints are weak
        if chunk.get("hint_confidence", 0.0) >= 0.4:
            continue

        try:
            prompt = llm_prompt.format(
                stages=stages_str,
                lobs=lobs_str,
                screens=screens_str,
                chunk_text=chunk["text"][:300]
            )

            response = llm_complete(prompt=prompt, system="You are a CAS domain classifier.", max_tokens=200)

            try:
                # Extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    result = json.loads(json_str)

                    # Merge LLM results
                    chunk['stage_hint'] = result.get('stage_hint') or chunk.get('stage_hint')
                    chunk['lob_hint'] = result.get('lob_hint') or chunk.get('lob_hint')
                    chunk['screen_hint'] = result.get('screen_hint') or chunk.get('screen_hint')
                    chunk['chunk_type'] = result.get('chunk_type', chunk.get('chunk_type'))
                    chunk['hint_confidence'] = float(result.get('confidence', chunk.get('hint_confidence', 0.0)))
                    updated += 1
            except json.JSONDecodeError:
                pass  # Keep Python guess

        except LLMNotLoadedError:
            # LLM not available; downgrade confidence
            chunk['hint_confidence'] = 0.2
        except Exception as e:
            logger.warning(f"LLM call failed: {e}")

    if updated > 0:
        logger.info(f"[LLM] Enhanced {updated} ambiguous chunks")

    return chunks


def generate_markdown_wiki(chunks: List[Dict], taxonomy: TaxonomyLoader, module: str) -> None:
    """Generate human-readable markdown wiki from chunks."""
    wiki_dir = Path("data/knowledge") / module
    wiki_dir.mkdir(parents=True, exist_ok=True)

    stages_dir = wiki_dir / "stages"
    screens_dir = wiki_dir / "screens"
    concepts_dir = wiki_dir / "concepts"

    for d in [stages_dir, screens_dir, concepts_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Group chunks
    chunks_by_stage = defaultdict(list)
    chunks_by_screen = defaultdict(list)
    chunks_by_lob = defaultdict(list)

    for chunk in chunks:
        if chunk.get('stage_hint'):
            chunks_by_stage[chunk['stage_hint']].append(chunk)
        if chunk.get('screen_hint'):
            chunks_by_screen[chunk['screen_hint']].append(chunk)
        if chunk.get('lob_hint'):
            chunks_by_lob[chunk['lob_hint']].append(chunk)

    # Write stage markdown
    for stage_name, stage_chunks in chunks_by_stage.items():
        slug = slugify(stage_name)
        md_path = stages_dir / f"{slug}.md"

        # Find stage entry for metadata
        stage_entry = next((s for s in taxonomy.stages['entries'] if s.get('name') == stage_name), {})
        page_range = f"{stage_entry.get('page_start')}-{stage_entry.get('page_end')}" if stage_entry.get('page_start') else "N/A"

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {stage_name}\n\n")
            f.write(f"**Stage ID:** {slug}\n")
            f.write(f"**Source pages:** {page_range}\n\n")
            f.write("## Knowledge Chunks\n\n")

            for chunk in stage_chunks[:20]:  # Limit to first 20
                f.write(f"### {chunk.get('section_title', 'Section')}\n")
                f.write(f"> {chunk['text'][:400]}...\n\n")

    # Write screen markdown
    for screen_name, screen_chunks in chunks_by_screen.items():
        slug = slugify(screen_name)
        md_path = screens_dir / f"{slug}.md"

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {screen_name}\n\n")
            f.write(f"**Appears in {len(screen_chunks)} knowledge chunks**\n\n")
            f.write("## Knowledge Chunks\n\n")

            for chunk in screen_chunks[:20]:
                f.write(f"### {chunk.get('section_title', 'Section')}\n")
                f.write(f"> {chunk['text'][:400]}...\n\n")

    # Write LOB markdown
    for lob_name, lob_chunks in chunks_by_lob.items():
        slug = slugify(lob_name)
        md_path = concepts_dir / f"lob_{slug}.md"

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {lob_name}\n\n")
            f.write(f"**Product Type / Line of Business**\n\n")
            f.write(f"**Appears in {len(lob_chunks)} knowledge chunks**\n\n")
            f.write("## Knowledge Chunks\n\n")

            for chunk in lob_chunks[:20]:
                f.write(f"### {chunk.get('section_title', 'Section')}\n")
                f.write(f"> {chunk['text'][:400]}...\n\n")

    logger.info(f"[OK] Wiki pages written: {len(chunks_by_stage)} stages, {len(chunks_by_screen)} screens, {len(chunks_by_lob)} LOBs")


def detect_unknowns(chunks: List[Dict], taxonomy: TaxonomyLoader, module: str) -> None:
    """Track chunks with unmatched section titles -> review candidates."""
    unknowns = []
    section_titles_seen = set()

    for chunk in chunks:
        section = chunk.get('section_title', '').lower()
        if section and section not in section_titles_seen:
            # Check if title is in taxonomy
            if section not in taxonomy.screens['all_map'] and section not in taxonomy.stages['all_map']:
                unknowns.append({
                    'section_title': chunk.get('section_title'),
                    'page_range': chunk.get('page_range'),
                    'reason': 'not_in_taxonomy'
                })
                section_titles_seen.add(section)

    if unknowns:
        candidates_file = Path("data/knowledge") / module / f"{module}_review_candidates.toml"
        with open(candidates_file, 'w', encoding='utf-8') as f:
            f.write(f"# Unknown sections from {module} PDF — review for new screens/stages\n\n")
            for unknown in unknowns:
                f.write(f"[[candidate]]\n")
                f.write(f'section_title = "{unknown["section_title"]}"\n')
                f.write(f'page_range = "{unknown["page_range"]}"\n')
                f.write(f'reason = "{unknown["reason"]}"\n\n')

        logger.info(f"[OK] Review candidates: {len(unknowns)} unknowns → {candidates_file}")


def build_knowledge(module: str = "cas", rebuild: bool = False):
    """Main function to build module knowledge wiki."""
    settings = get_settings()

    # Load taxonomy
    taxonomy = TaxonomyLoader(module)
    if not taxonomy.load():
        logger.error("Failed to load taxonomy. Aborting.")
        return False

    # Discover PDFs
    pdf_dir = Path("data/knowledge") / module / "_source"
    if not pdf_dir.exists():
        logger.warning(f"PDF source directory not found: {pdf_dir}")
        return False

    pdf_files = list(pdf_dir.glob("**/*.pdf"))
    if not pdf_files:
        logger.info(f"No PDF files found in {pdf_dir}")
        return True  # Not an error

    logger.info(f"[OK] Found {len(pdf_files)} PDF(s)")

    # Extract chunks
    all_chunks = []
    for pdf_path in pdf_files:
        logger.info(f"Extracting: {pdf_path.name}...")
        chunks = extract_pdf_chunks(pdf_path, taxonomy)
        all_chunks.extend(chunks)
        logger.info(f"  → {len(chunks)} chunks")

    if not all_chunks:
        logger.warning("No chunks extracted from PDFs")
        return False

    logger.info(f"[OK] Total chunks: {len(all_chunks)}")

    # Hybrid hints: Python + LLM
    all_chunks = apply_llm_hints(all_chunks, taxonomy)

    # Log population
    chunks_with_stage = sum(1 for c in all_chunks if c.get('stage_hint'))
    chunks_with_screen = sum(1 for c in all_chunks if c.get('screen_hint'))
    chunks_with_lob = sum(1 for c in all_chunks if c.get('lob_hint'))

    logger.info(f"[OK] Stage hints: {chunks_with_stage}/{len(all_chunks)} ({100*chunks_with_stage/len(all_chunks):.1f}%)")
    logger.info(f"[OK] Screen hints: {chunks_with_screen}/{len(all_chunks)} ({100*chunks_with_screen/len(all_chunks):.1f}%)")
    logger.info(f"[OK] LOB hints: {chunks_with_lob}/{len(all_chunks)} ({100*chunks_with_lob/len(all_chunks):.1f}%)")

    # Embed
    logger.info(f"Loading embedding model...")
    model = SentenceTransformer(str(settings.embedding_model))

    logger.info(f"Embedding {len(all_chunks)} chunks...")
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=256)
    embeddings = embeddings.astype(np.float32)

    # Build FAISS (module-scoped)
    logger.info("Building FAISS index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss_dir = Path(settings.faiss_index_dir)
    faiss_dir.mkdir(parents=True, exist_ok=True)
    knowledge_path = faiss_dir / f"{module}_knowledge.faiss"
    faiss.write_index(index, str(knowledge_path))
    logger.info(f"[OK] FAISS index: {knowledge_path}")

    # Generate wiki
    generate_markdown_wiki(all_chunks, taxonomy, module)

    # Detect unknowns
    detect_unknowns(all_chunks, taxonomy, module)

    # Store in DB
    logger.info("Storing chunks in database...")
    conn = get_conn()
    try:
        with get_cursor(conn) as cur:
            if rebuild:
                cur.execute("DELETE FROM doc_chunks WHERE source_module = %s", (module,))
                logger.info(f"Cleared existing {module} chunks")

            for faiss_pos, chunk in enumerate(all_chunks):
                cur.execute(
                    """
                    INSERT INTO doc_chunks
                    (chunk_id, doc_path, section_title, stage_hint, screen_hint, lob_hint,
                     chunk_type, hint_confidence, source_module, text, page_range, token_count, faiss_pos)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        chunk["chunk_id"],
                        chunk["doc_path"],
                        chunk["section_title"],
                        chunk.get("stage_hint"),
                        chunk.get("screen_hint"),
                        chunk.get("lob_hint"),
                        chunk.get("chunk_type"),
                        chunk.get("hint_confidence"),
                        module,
                        chunk["text"],
                        chunk["page_range"],
                        chunk["token_count"],
                        faiss_pos,
                    ),
                )
        conn.commit()
        logger.info(f"[OK] DB: {len(all_chunks)} rows inserted")
    finally:
        release_conn(conn)

    logger.info(f"[OK] {module.upper()} knowledge wiki build complete")
    return True


def main():
    parser = argparse.ArgumentParser(description='Build knowledge wiki from seed taxonomy + PDFs')
    parser.add_argument('--module', default='cas', help='Module name (default: cas)')
    parser.add_argument('--rebuild', action='store_true', help='Delete existing module chunks before inserting')

    args = parser.parse_args()

    success = build_knowledge(module=args.module, rebuild=args.rebuild)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
