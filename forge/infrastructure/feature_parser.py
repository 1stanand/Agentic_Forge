"""Feature parser - Complete Gherkin parsing for CAS ATDD repository.

Handles all CAS extensions: dictionaries, annotations, Background, Scenario Outlines,
Examples, doc strings, LogicalIDs, and flow_type detection.

Calls infer_screen_contexts() after parsing each scenario to populate screen_context.
"""

import os
import re
import logging
from typing import Optional

from forge.infrastructure.normalisation import STEP_KEYWORD_MAP, _norm
from forge.infrastructure.screen_context import infer_screen_contexts

logger = logging.getLogger(__name__)

# Regex patterns
_DICT_RE = re.compile(r'\$\{(\w+)\s*=\s*\[(.*?)\]\}', re.IGNORECASE | re.DOTALL)
_ANNOTATION_RE = re.compile(r'^\s*@(.+)')
_KEYWORD_RE = re.compile(
    r'^\s*(Feature|Background|Scenario Outline|Scenario|Examples?|Given|When|Then|And|But|\*)\s*:?\s*(.*)',
    re.IGNORECASE
)
_TABLE_ROW_RE = re.compile(r'^\s*\|')
_DOC_STRING_RE = re.compile(r'^\s*("""|\'\'\')(.*)')


def _read_lines(file_path: str) -> list:
    """Read file with BOM, CRLF normalization, and error handling."""
    with open(file_path, encoding="utf-8-sig", errors="replace") as fh:
        content = fh.read()
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    return content.split("\n")


def _is_dict_line(line: str) -> bool:
    return bool(_DICT_RE.search(line))


def _is_annotation_line(line: str) -> bool:
    return bool(_ANNOTATION_RE.match(line))


def _is_comment(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("#") and not _DICT_RE.search(stripped)


def _parse_annotations(lines: list) -> list:
    """Extract @annotation strings from lines."""
    result = []
    for line in lines:
        m = _ANNOTATION_RE.match(line)
        if m:
            tag = m.group(1).strip()
            if tag:
                result.append("@" + tag)
    return result


def _parse_dicts(lines: list) -> dict:
    """Extract #${Key=["v1","v2"]} definitions from lines."""
    result = {}
    for line in lines:
        for m in _DICT_RE.finditer(line):
            key = m.group(1).strip()
            raw_values = m.group(2)
            values = []
            for token in raw_values.split(","):
                v = token.strip().strip('"').strip("'").strip()
                if v:
                    values.append(v)
            result[key] = values
    return result


def _check_conflict(file_annotations: list, file_dicts: dict) -> bool:
    """Check if file has both @Order/@E2EOrder AND dictionaries (invalid)."""
    has_order = any(
        ann.lower() in ("@order", "@e2eorder")
        for ann in file_annotations
    )
    return has_order and bool(file_dicts)


def _normalise_keyword(raw: str) -> str:
    """Convert raw keyword to canonical form."""
    return STEP_KEYWORD_MAP.get(raw.strip().lower(), raw.strip().capitalize())


def _classify(line: str) -> tuple:
    """Classify line type and extract keyword/text."""
    stripped = line.strip()

    if not stripped:
        return ("blank", "", "")

    if _is_dict_line(line):
        return ("dict", "", stripped)

    if stripped.startswith("#"):
        return ("comment", "", stripped)

    if stripped.startswith("@"):
        return ("annotation", "", stripped)

    if _TABLE_ROW_RE.match(line):
        return ("table_row", "", stripped)

    doc_m = _DOC_STRING_RE.match(line)
    if doc_m:
        return ("doc_string", doc_m.group(1), doc_m.group(2).strip())

    kw_m = _KEYWORD_RE.match(line)
    if kw_m:
        raw_kw = kw_m.group(1).strip()
        rest = kw_m.group(2).strip()
        kw_lower = raw_kw.lower()

        if kw_lower == "feature":
            return ("feature", raw_kw, rest)
        if kw_lower == "background":
            return ("background", raw_kw, rest)
        if kw_lower == "scenario outline":
            return ("outline", raw_kw, rest)
        if kw_lower == "scenario":
            return ("scenario", raw_kw, rest)
        if kw_lower in ("examples", "example"):
            return ("examples", raw_kw, rest)
        if kw_lower in ("given", "when", "then", "and", "but", "*"):
            return ("step", raw_kw, rest)

    return ("other", "", stripped)


def _parse_table_row(line: str) -> list:
    """Parse table row | col1 | col2 |."""
    inner = line.strip().strip("|")
    return [cell.strip() for cell in inner.split("|")]


def parse_file(file_path: str) -> dict:
    """Parse .feature file and return structured data."""
    file_name = os.path.basename(file_path)

    result = {
        "file_path": file_path,
        "file_name": file_name,
        "folder_path": os.path.dirname(file_path),
        "feature_title": None,
        "file_tags": [],
        "file_dicts": {},
        "flow_type": "unordered",
        "has_conflict": False,
        "parse_error": None,
        "scenarios": [],
    }

    try:
        lines = _read_lines(file_path)
    except Exception as exc:
        result["parse_error"] = f"read error: {exc}"
        return result

    if not any(l.strip() for l in lines):
        result["parse_error"] = "empty file"
        return result

    try:
        _parse_lines(lines, result)
    except Exception as exc:
        logger.exception(f"Parse error in {file_path}: {exc}")
        result["parse_error"] = f"parse error: {exc}"

    return result


def _parse_lines(lines: list, result: dict) -> None:
    """Parse lines into result dict."""
    STATE_FILE_HEADER = "FILE_HEADER"
    STATE_IN_SCENARIO = "IN_SCENARIO"
    STATE_IN_EXAMPLES = "IN_EXAMPLES"
    STATE_IN_DOCSTRING = "IN_DOCSTRING"

    state = STATE_FILE_HEADER

    pending_annotations = []
    pending_dict_lines = []

    current_scenario = None
    current_example = None
    current_step = None

    doc_string_delimiter = None
    doc_string_lines = []

    background_steps = []
    in_background = False

    scenario_index = 0

    def flush_pending():
        nonlocal pending_annotations, pending_dict_lines
        anns = _parse_annotations(pending_annotations)
        dicts = _parse_dicts(pending_dict_lines)
        pending_annotations = []
        pending_dict_lines = []
        return anns, dicts

    def close_step():
        nonlocal current_step
        if current_step is not None and current_scenario is not None:
            current_scenario["steps"].append(current_step)
            current_step = None

    def close_example():
        nonlocal current_example
        if current_example is not None and current_scenario is not None:
            current_scenario["example_blocks"].append(current_example)
            current_example = None

    def close_scenario():
        nonlocal current_scenario, in_background, background_steps
        if current_scenario is None:
            return

        close_step()
        close_example()

        # CRITICAL: Call screen context inference after parsing scenario
        infer_screen_contexts(current_scenario["steps"])

        if in_background:
            background_steps = list(current_scenario["steps"])
            in_background = False
        else:
            # Prepend background steps if present
            if background_steps:
                bg = []
                for i, s in enumerate(background_steps):
                    bg.append({
                        "keyword": s["keyword"],
                        "step_text": s["step_text"],
                        "step_position": i,
                        "screen_context": s.get("screen_context"),
                    })
                offset = len(bg)
                for s in current_scenario["steps"]:
                    s["step_position"] += offset
                current_scenario["steps"] = bg + current_scenario["steps"]
                # Re-infer screen context on combined steps
                infer_screen_contexts(current_scenario["steps"])

            result["scenarios"].append(current_scenario)

        current_scenario = None

    def open_scenario(title: str, is_outline: bool, anns: list, dicts: dict):
        nonlocal current_scenario, scenario_index
        close_scenario()
        current_scenario = {
            "title": title,
            "scenario_type": "Scenario Outline" if is_outline else "Scenario",
            "is_outline": is_outline,
            "scenario_annotations": anns,
            "scenario_dicts": dicts,
            "scenario_index": scenario_index,
            "steps": [],
            "example_blocks": [],
        }
        scenario_index += 1

    def open_example(anns: list, dicts: dict, idx: int):
        nonlocal current_example
        close_example()
        current_example = {
            "block_annotations": anns,
            "block_dicts": dicts,
            "headers": [],
            "rows": [],
            "block_index": idx,
            "_header_set": False,
        }

    # Main parsing loop
    feature_seen = False

    for raw_line in lines:
        line = raw_line.rstrip()
        lt, kw, rest = _classify(line)

        # Doc-string mode
        if state == STATE_IN_DOCSTRING:
            if lt == "doc_string" and kw == doc_string_delimiter:
                if current_step is not None:
                    current_step["step_text"] += "\n" + "\n".join(doc_string_lines)
                doc_string_lines = []
                doc_string_delimiter = None
                state = STATE_IN_SCENARIO
            else:
                doc_string_lines.append(line)
            continue

        # Opening doc string
        if lt == "doc_string":
            doc_string_delimiter = kw
            doc_string_lines = []
            state = STATE_IN_DOCSTRING
            continue

        # File header (before Feature:)
        if state == STATE_FILE_HEADER:
            if lt == "feature":
                if not feature_seen:
                    feature_seen = True
                    result["feature_title"] = rest if rest else None
                    anns, dicts = flush_pending()
                    result["file_tags"] = anns
                    result["file_dicts"] = dicts

                    # Detect flow type
                    lower_anns = [a.lower() for a in anns]
                    if "@order" in lower_anns:
                        result["flow_type"] = "ordered"
                    elif "@e2eorder" in lower_anns:
                        result["flow_type"] = "ordered"

                    result["has_conflict"] = _check_conflict(anns, dicts)
                    if result["has_conflict"]:
                        logger.warning(f"{file_path}: both @Order and dictionaries (invalid)")

                    state = STATE_IN_SCENARIO
                else:
                    logger.warning(f"{file_path}: duplicate Feature: line")
                continue

            if lt == "annotation":
                pending_annotations.append(line)
            elif lt == "dict":
                pending_dict_lines.append(line)
            elif lt not in ("blank", "comment"):
                pass
            continue

        # In scenario body
        if state in (STATE_IN_SCENARIO, STATE_IN_EXAMPLES):

            if lt == "background":
                close_scenario()
                in_background = True
                open_scenario("__background__", False, [], {})
                state = STATE_IN_SCENARIO
                continue

            if lt in ("scenario", "outline"):
                anns, dicts = flush_pending()
                is_outline = (lt == "outline")
                open_scenario(rest, is_outline, anns, dicts)
                state = STATE_IN_SCENARIO
                continue

            if lt == "examples":
                if current_scenario is None:
                    logger.warning(f"{file_path}: Examples outside scenario")
                    continue
                if not current_scenario.get("is_outline"):
                    logger.warning(f"{file_path}: Examples in non-outline scenario")

                close_step()
                anns, dicts = flush_pending()
                block_index = len(current_scenario["example_blocks"])
                if current_example is not None:
                    close_example()
                open_example(anns, dicts, block_index)
                state = STATE_IN_EXAMPLES
                continue

            if lt == "step":
                if current_scenario is None:
                    continue

                close_step()
                pos = len(current_scenario["steps"])
                canonical_kw = _normalise_keyword(kw)
                current_step = {
                    "keyword": canonical_kw,
                    "step_text": rest,
                    "step_position": pos,
                    "screen_context": None,
                }
                continue

            if lt == "table_row":
                if state == STATE_IN_EXAMPLES and current_example is not None:
                    if not current_example["_header_set"]:
                        current_example["headers"] = _parse_table_row(line)
                        current_example["_header_set"] = True
                    else:
                        cells = _parse_table_row(line)
                        headers = current_example["headers"]
                        while len(cells) < len(headers):
                            cells.append("")
                        row_dict = {headers[i]: cells[i] for i in range(len(headers))}
                        current_example["rows"].append(row_dict)
                elif current_step is not None:
                    current_step["step_text"] += "\n" + line.strip()
                continue

            if lt == "annotation":
                pending_annotations.append(line)
            elif lt == "dict":
                pending_dict_lines.append(line)

    # Final cleanup
    close_scenario()
