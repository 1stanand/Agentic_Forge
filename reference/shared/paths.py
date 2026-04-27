from __future__ import annotations

from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
ASSETS_ROOT = PROJECT_ROOT / "assets"
CONFIG_DIR = PROJECT_ROOT / "config"
DOMAIN_CONFIG_DIR = CONFIG_DIR / "domain"
GENERATION_CONFIG_DIR = CONFIG_DIR / "generation"
WORKFLOW_CONFIG_DIR = CONFIG_DIR / "workflow"
TOOLS_ROOT = PROJECT_ROOT / "tools"
WORKSPACE_ROOT = PROJECT_ROOT / "workspace"
DOCS_ROOT = PROJECT_ROOT / "docs"
TEST_ROOT = PROJECT_ROOT / "test"

TEMPLATES_DIR = ASSETS_ROOT / "templates"
PROMPTS_DIR = ASSETS_ROOT / "prompts"
WORKFLOW_ASSETS_DIR = ASSETS_ROOT / "workflow"
GENERATION_ASSETS_DIR = GENERATION_CONFIG_DIR
ORDER_JSON_PATH = WORKFLOW_CONFIG_DIR / "order.json"
DOMAIN_KNOWLEDGE_TOML_PATH = DOMAIN_CONFIG_DIR / "domain_knowledge.toml"
DOMAIN_VOCABULARY_TOML_PATH = DOMAIN_CONFIG_DIR / "domain_vocabulary.toml"
RULE_GUIDANCE_TOML_PATH = DOMAIN_CONFIG_DIR / "rule_guidance.toml"
SCREEN_METADATA_TOML_PATH = DOMAIN_CONFIG_DIR / "screen_metadata.toml"
STAGE_METADATA_TOML_PATH = DOMAIN_CONFIG_DIR / "stage_metadata.toml"
KNOWN_TRUE_STEPS_TOML_PATH = DOMAIN_CONFIG_DIR / "known_true_steps.toml"
CAS_SCREEN_FIELDS_TOML_PATH = DOMAIN_CONFIG_DIR / "cas_screen_fields.toml"
CAS_STAGE_RULES_TOML_PATH = DOMAIN_CONFIG_DIR / "cas_stage_rules.toml"
CAS_ENTITY_BEHAVIORS_TOML_PATH = DOMAIN_CONFIG_DIR / "cas_entity_behaviors.toml"
PLANNER_HINTS_TOML_PATH = GENERATION_CONFIG_DIR / "planner_hints.toml"
ASSEMBLER_HINTS_TOML_PATH = GENERATION_CONFIG_DIR / "assembler_hints.toml"
RETRIEVAL_SETTINGS_TOML_PATH = GENERATION_CONFIG_DIR / "retrieval_settings.toml"

SAMPLES_DIR = WORKSPACE_ROOT / "samples"

GENERATED_ROOT = WORKSPACE_ROOT / "generated"
DEFAULT_OUTPUT_DIR = GENERATED_ROOT / "output"
DEFAULT_OUTPUT_FINAL_DIR = GENERATED_ROOT / "output_final"
DEFAULT_OUTPUT_ORDERED_DIR = GENERATED_ROOT / "output_ordered"
DEFAULT_OUTPUT_UNORDERED_DIR = GENERATED_ROOT / "output_unordered"

INDEX_DIR = WORKSPACE_ROOT / "index"
SCRATCH_DIR = WORKSPACE_ROOT / "scratch"

WEB_ROOT = SRC_ROOT / "casforge" / "web"
WEB_FRONTEND_DIR = WEB_ROOT / "frontend"

STORAGE_ROOT = SRC_ROOT / "casforge" / "storage"
SCHEMA_SQL_PATH = STORAGE_ROOT / "schema.sql"
CREATE_VIEWS_SQL_PATH = STORAGE_ROOT / "CreateViews.sql"

# Phase 1: CAS Knowledge Index
CAS_KNOWLEDGE_INDEX_DIR = INDEX_DIR / "cas_knowledge"
CAS_KNOWLEDGE_CHUNKS_JSONL = SCRATCH_DIR / "pdf_help_ingest" / "pages.jsonl"
CAS_KNOWLEDGE_SCHEMA_PATH = STORAGE_ROOT / "schema_v2_knowledge.sql"


def resolve_user_path(path: str | Path, base: Optional[str | Path] = None) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate.resolve()
    anchor = Path(base).resolve() if base is not None else PROJECT_ROOT
    return (anchor / candidate).resolve()


def ensure_dir(path: str | Path) -> Path:
    resolved = Path(path)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved
