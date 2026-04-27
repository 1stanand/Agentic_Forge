from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from casforge.domain.knowledge import load_domain_vocabulary
from casforge.domain.runtime_context import load_screen_metadata, load_stage_metadata


_SPACE_RE = re.compile(r"\s+")
_PARENS_RE = re.compile(r"\(([^)]*)\)")
_GENERIC_SCREEN_WORDS = {
    "section",
    "screen",
    "page",
    "tab",
    "grid",
    "details",
    "applications",
    "application",
    "actions",
    "summary",
    "history",
}


def _norm(text: str) -> str:
    return _SPACE_RE.sub(" ", str(text or "").strip().lower())


def _slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", _norm(text)).strip("-")
    return value or "untitled"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _label_variants(label: str) -> list[str]:
    label = str(label or "").strip()
    out = {_norm(label)}
    no_parens = re.sub(r"\([^)]*\)", "", label).strip()
    if no_parens:
        out.add(_norm(no_parens))
    for token in _PARENS_RE.findall(label):
        token = token.strip()
        if token and token.isupper() and len(token) <= 8:
            out.add(_norm(token))
    squashed = (
        label.replace("Activity", " Activity")
        .replace("CreditCard", "Credit Card")
        .replace("ConsumerFinance", "Consumer Finance")
        .replace("ManagementSystem", "Management System")
        .replace("InvestigationVerification", "Investigation Verification")
        .replace("InvestigationCompletion", "Investigation Completion")
        .replace("InvestigationInitiation", "Investigation Initiation")
        .replace("Data Entry(CCDE)", "Data Entry (CCDE)")
    )
    out.add(_norm(squashed))
    no_parens = re.sub(r"\([^)]*\)", "", squashed).strip()
    if no_parens:
        out.add(_norm(no_parens))
    return [item for item in out if item]


def _first_match_page(pages: list[dict[str, Any]], label: str, min_page: int = 4) -> int | None:
    variants = _label_variants(label)
    for row in pages:
        page_no = int(row["page"])
        if page_no < min_page:
            continue
        heading = _norm(row.get("heading") or "")
        lead = _norm((row.get("text") or "")[:450])
        for variant in variants:
            if not variant:
                continue
            if heading == variant or heading.startswith(f"{variant} ") or lead.startswith(variant):
                return page_no
            if f"\n{variant} " in f"\n{_norm(row.get('text') or '')[:600]} ":
                return page_no
    return None


def detect_toc_section_starts(pages: list[dict[str, Any]], toc_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    starts: list[dict[str, Any]] = []
    min_page = 4
    for item in toc_rows:
        label = str(item.get("label") or "").strip()
        if not label:
            continue
        page_no = _first_match_page(pages, label, min_page=min_page)
        if page_no is None:
            continue
        starts.append({"label": label, "page_start": page_no})
        min_page = max(min_page, page_no + 1)
    deduped: list[dict[str, Any]] = []
    seen_pages: set[int] = set()
    for item in sorted(starts, key=lambda row: (int(row["page_start"]), row["label"])):
        page_no = int(item["page_start"])
        if page_no in seen_pages:
            continue
        deduped.append(item)
        seen_pages.add(page_no)
    return deduped


def build_section_spans(pages: list[dict[str, Any]], toc_starts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not toc_starts:
        return [{"label": "CAS Help Corpus", "page_start": 1, "page_end": len(pages)}]
    spans: list[dict[str, Any]] = []
    sorted_starts = sorted(toc_starts, key=lambda row: int(row["page_start"]))
    if sorted_starts[0]["page_start"] > 1:
        spans.append(
            {
                "label": "Front Matter",
                "page_start": 1,
                "page_end": int(sorted_starts[0]["page_start"]) - 1,
            }
        )
    for idx, item in enumerate(sorted_starts):
        start = int(item["page_start"])
        end = len(pages)
        if idx + 1 < len(sorted_starts):
            end = int(sorted_starts[idx + 1]["page_start"]) - 1
        if end < start:
            continue
        spans.append({"label": item["label"], "page_start": start, "page_end": end})
    return spans


def _screen_lexicon() -> dict[str, str]:
    out: dict[str, str] = {}
    for canonical, spec in (load_screen_metadata() or {}).items():
        out[_norm(canonical)] = canonical
        for alias in spec.get("aliases") or []:
            alias_text = _norm(alias)
            if alias_text:
                out[alias_text] = canonical
        for phrase in spec.get("phrase_hints") or []:
            phrase_text = _norm(phrase)
            if phrase_text:
                out[phrase_text] = canonical
    return out


def _stage_lexicon() -> dict[str, str]:
    out: dict[str, str] = {}
    vocab = load_domain_vocabulary()
    for canonical in (load_stage_metadata() or {}).keys():
        out[_norm(canonical)] = canonical
    for row in vocab.get("stages") or []:
        canonical = str(row.get("canonical") or "").strip()
        if not canonical:
            continue
        out[_norm(canonical)] = canonical
        for alias in row.get("aliases") or []:
            alias_text = _norm(alias)
            if alias_text:
                out[alias_text] = canonical
    return out


def _known_stage_context(section_label: str, text: str) -> list[str]:
    stage_lex = _stage_lexicon()
    matched: list[str] = []
    haystack = f"{_norm(section_label)} {_norm(text)}"
    for alias, canonical in stage_lex.items():
        if alias and f" {alias} " in f" {haystack} " and canonical not in matched:
            matched.append(canonical)
    return matched[:6]


def _known_screen_context(text: str) -> list[str]:
    screen_lex = _screen_lexicon()
    matched: list[str] = []
    haystack = _norm(text)
    for alias, canonical in screen_lex.items():
        if alias and f" {alias} " in f" {haystack} " and canonical not in matched:
            matched.append(canonical)
    return matched[:8]


def _discover_additional_screen_candidates(text: str) -> list[str]:
    candidates = re.findall(r"\b([A-Z][A-Za-z/&,'() -]{2,80})\s+(?:tab|page|screen|section|grid)\b", text)
    out: list[str] = []
    for item in candidates:
        name = _SPACE_RE.sub(" ", item.strip())
        low = _norm(name)
        if not low or low in _GENERIC_SCREEN_WORDS:
            continue
        if low.startswith(("use this", "on the", "click", "to ", "in the", "this ")):
            continue
        pretty = name.strip(" -")
        if pretty and pretty not in out:
            out.append(pretty)
    return out[:8]


def build_chunks(
    pages: list[dict[str, Any]],
    section_spans: list[dict[str, Any]],
    chunk_dir: Path,
    target_chunks: int = 100,
) -> list[dict[str, Any]]:
    total_pages = len(pages)
    chunk_size = max(6, math.ceil(total_pages / max(target_chunks, 1)))
    manifest: list[dict[str, Any]] = []
    chunk_counter = 1
    for section in section_spans:
        label = str(section["label"])
        start = int(section["page_start"])
        end = int(section["page_end"])
        page_no = start
        while page_no <= end:
            chunk_start = page_no
            chunk_end = min(end, chunk_start + chunk_size - 1)
            page_rows = pages[chunk_start - 1:chunk_end]
            text = "\n\n".join(row["text"] for row in page_rows if row.get("text"))
            stage_context = _known_stage_context(label, text)
            screen_context = _known_screen_context(text)
            inferred_screens = _discover_additional_screen_candidates(text)
            chunk_id = f"cas_chunk_{chunk_counter:03d}"
            title = f"{label} [{chunk_start}-{chunk_end}]"
            filename = f"{chunk_id}_{_slug(label)}_{chunk_start:03d}_{chunk_end:03d}.md"
            path = chunk_dir / filename
            content = [
                f"# {title}",
                "",
                f"- chunk_id: `{chunk_id}`",
                f"- section_label: `{label}`",
                f"- page_range: `{chunk_start}-{chunk_end}`",
                f"- stage_context: `{', '.join(stage_context) if stage_context else ''}`",
                f"- known_screen_context: `{', '.join(screen_context) if screen_context else ''}`",
                f"- inferred_screen_candidates: `{', '.join(inferred_screens) if inferred_screens else ''}`",
                "",
                "## Text",
                "",
                text.strip(),
                "",
            ]
            path.write_text("\n".join(content), encoding="utf-8")
            manifest.append(
                {
                    "chunk_id": chunk_id,
                    "title": title,
                    "section_label": label,
                    "page_start": chunk_start,
                    "page_end": chunk_end,
                    "page_count": chunk_end - chunk_start + 1,
                    "stage_context": stage_context,
                    "screen_context": screen_context,
                    "inferred_screen_candidates": inferred_screens,
                    "word_count": len(text.split()),
                    "path": str(path),
                }
            )
            chunk_counter += 1
            page_no = chunk_end + 1
    return manifest


def build_chunk_index(manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in manifest:
        out.append(
            {
                "chunk_id": row["chunk_id"],
                "title": row["title"],
                "section_label": row["section_label"],
                "page_start": row["page_start"],
                "page_end": row["page_end"],
                "page_count": row["page_count"],
                "stage_context": row["stage_context"],
                "screen_context": row["screen_context"],
                "inferred_screen_candidates": row["inferred_screen_candidates"],
                "word_count": row["word_count"],
                "path": row["path"],
            }
        )
    return out


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def build_quality_report(
    manifest: list[dict[str, Any]],
    toc_rows: list[dict[str, Any]],
    toc_starts: list[dict[str, Any]],
    total_pages: int,
) -> str:
    section_count = len({row["section_label"] for row in manifest})
    page_coverage = sum(row["page_count"] for row in manifest)
    missing = []
    start_labels = {row["label"] for row in toc_starts}
    for item in toc_rows:
        label = str(item.get("label") or "").strip()
        if label and label not in start_labels:
            missing.append(label)
    stage_counter = Counter()
    screen_counter = Counter()
    for row in manifest:
        stage_counter.update(row["stage_context"])
        screen_counter.update(row["screen_context"])
    lines = [
        "# Extraction Quality Report",
        "",
        f"- total_pages: `{total_pages}`",
        f"- chunk_count: `{len(manifest)}`",
        f"- section_count: `{section_count}`",
        f"- page_coverage_from_manifest: `{page_coverage}`",
        f"- avg_pages_per_chunk: `{round(page_coverage / max(len(manifest), 1), 2)}`",
        "",
        "## TOC labels without detected section starts",
        "",
    ]
    if missing:
        for label in missing:
            lines.append(f"- `{label}`")
    else:
        lines.append("- None")
    lines.extend(["", "## Most common stage context", ""])
    for name, count in stage_counter.most_common(20):
        lines.append(f"- `{name}`: {count}")
    lines.extend(["", "## Most common known screen context", ""])
    for name, count in screen_counter.most_common(20):
        lines.append(f"- `{name}`: {count}")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a readable chunk corpus from the extracted CAS help PDF pages.")
    parser.add_argument("--pages", required=True, help="Path to pages.jsonl")
    parser.add_argument("--toc", required=True, help="Path to toc_stage_candidates.json")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--target-chunks", type=int, default=100, help="Approximate chunk count")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pages_path = (ROOT / args.pages).resolve() if not Path(args.pages).is_absolute() else Path(args.pages).resolve()
    toc_path = (ROOT / args.toc).resolve() if not Path(args.toc).is_absolute() else Path(args.toc).resolve()
    out_dir = (ROOT / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out).resolve()
    chunks_dir = out_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    pages = _read_jsonl(pages_path)
    toc_rows = _read_json(toc_path)
    toc_starts = detect_toc_section_starts(pages, toc_rows)
    section_spans = build_section_spans(pages, toc_starts)
    manifest = build_chunks(pages, section_spans, chunks_dir, target_chunks=args.target_chunks)
    chunk_index = build_chunk_index(manifest)

    write_json(out_dir / "detected_toc_starts.json", toc_starts)
    write_json(out_dir / "section_spans.json", section_spans)
    write_json(out_dir / "chunk_manifest.json", manifest)
    write_jsonl(out_dir / "chunk_index.jsonl", chunk_index)
    (out_dir / "extraction_quality_report.md").write_text(
        build_quality_report(manifest, toc_rows, toc_starts, len(pages)),
        encoding="utf-8",
    )

    print(f"Built {len(manifest)} chunks in {chunks_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
