"""
Verify Setup Script

Complete validation checklist for Forge Agentic deployment.
Exit code 0 = all checks passed
Exit code 1 = at least one critical check failed
"""

import sys
import logging
from pathlib import Path

from forge.core.config import get_settings
from forge.core.db import get_conn, get_cursor, release_conn
from forge.core.llm import get_llm, LLMNotLoadedError

logger = logging.getLogger(__name__)

# ANSI color codes for output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

# Track results
checks = []


def check(name: str, passed: bool, severity: str = "CRITICAL"):
    """Record a check result."""
    status = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
    severity_str = f"{RED}{severity}{RESET}" if not passed else severity

    print(f"{status} {name}")

    if not passed and severity == "CRITICAL":
        checks.append(("FAIL", name))
    elif not passed:
        checks.append(("WARN", name))
    else:
        checks.append(("PASS", name))


def main():
    """Run all verification checks."""

    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"Forge Agentic — Setup Verification")
    print(f"{GREEN}{'='*60}{RESET}\n")

    settings = get_settings()
    critical_failures = 0

    # 1. DATABASE CHECKS
    print(f"{GREEN}[DATABASE]{RESET}")
    try:
        conn = get_conn()
        try:
            with get_cursor(conn) as cursor:
                # Test connection
                cursor.execute("SELECT 1")
                check("DB connection", True)

                # Check all 12 tables exist
                tables_to_check = [
                    "users", "user_settings", "chat_sessions", "chat_messages",
                    "generation_jobs", "features", "scenarios", "steps",
                    "example_blocks", "unique_steps", "doc_chunks", "rag_cache"
                ]

                cursor.execute("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'
                    UNION
                    SELECT matviewname as table_name FROM pg_matviews
                    WHERE schemaname = 'public'
                """)

                existing_tables = {row['table_name'] for row in cursor.fetchall()}

                for table in tables_to_check:
                    table_exists = table in existing_tables
                    check(f"Table '{table}' exists", table_exists)
                    if not table_exists:
                        critical_failures += 1

                # Check row counts
                cursor.execute("SELECT COUNT(*) as cnt FROM unique_steps")
                result = cursor.fetchone()
                unique_steps_count = result['cnt'] if result else 0
                check(f"unique_steps populated ({unique_steps_count} rows)", unique_steps_count > 0)
                if unique_steps_count == 0:
                    critical_failures += 1

                cursor.execute("SELECT COUNT(*) as cnt FROM doc_chunks")
                result = cursor.fetchone()
                doc_chunks_count = result['cnt'] if result else 0
                check(f"doc_chunks populated ({doc_chunks_count} rows)", doc_chunks_count > 0)
                if doc_chunks_count == 0:
                    critical_failures += 1

        finally:
            release_conn(conn)

    except Exception as e:
        check(f"DB operations", False)
        logger.error(f"DB error: {e}")
        critical_failures += 1

    # 2. CONFIGURATION CHECKS
    print(f"\n{GREEN}[CONFIGURATION]{RESET}")

    check(f"DB name: {settings.db_name}", settings.db_name == "agentic_forge_local")
    check(f"DB host: {settings.db_host}:{settings.db_port}", bool(settings.db_host))

    check(f"LLM backend: {settings.llm_backend}", settings.llm_backend == "llama_cpp")
    check(f"MAX_CONCURRENT_JOBS: {settings.max_concurrent_jobs if hasattr(settings, 'max_concurrent_jobs') else 'NOT SET'}",
          hasattr(settings, 'max_concurrent_jobs') and settings.max_concurrent_jobs >= 1)

    # 3. PATH CHECKS
    print(f"\n{GREEN}[PATHS]{RESET}")

    paths = {
        "LLM model": Path(settings.llm_model_path),
        "Embedding model": Path(settings.embedding_model),
        "Cross-encoder model": Path(settings.cross_encoder_model),
        "Features repo": Path(settings.features_repo_path) if settings.features_repo_path else None,
        "Order.json": Path(settings.order_json_path) if settings.order_json_path else None,
        "CAS docs": Path(settings.cas_docs_path) if settings.cas_docs_path else None,
        "FAISS index dir": Path(settings.faiss_index_dir) if settings.faiss_index_dir else None,
        "Log path dir": Path(settings.log_path).parent,
    }

    for name, path in paths.items():
        if path is None:
            check(f"{name} set", False, "CRITICAL")
            critical_failures += 1
        elif path.exists():
            check(f"{name}: {path}", True)
        else:
            check(f"{name}: {path} (NOT FOUND)", False, "CRITICAL")
            critical_failures += 1

    # 4. FAISS INDICES CHECK
    print(f"\n{GREEN}[FAISS INDICES]{RESET}")

    faiss_dir = Path(settings.faiss_index_dir) if settings.faiss_index_dir else None
    if faiss_dir:
        step_index = faiss_dir / "faiss_index.bin"
        step_map = faiss_dir / "step_id_map.npy"
        knowledge_index = faiss_dir / "cas_knowledge.faiss"

        check(f"Step FAISS index: {step_index.name}", step_index.exists())
        if not step_index.exists():
            critical_failures += 1

        check(f"Step ID map: {step_map.name}", step_map.exists())
        if not step_map.exists():
            critical_failures += 1

        check(f"Knowledge FAISS index: {knowledge_index.name}", knowledge_index.exists())
        if not knowledge_index.exists():
            critical_failures += 1
    else:
        check("FAISS_INDEX_DIR not set", False, "CRITICAL")
        critical_failures += 1

    # 5. LLM CHECK
    print(f"\n{GREEN}[LLM]{RESET}")

    try:
        llm = get_llm()
        if llm is None:
            check("LLM loaded", False, "CRITICAL")
            critical_failures += 1
        else:
            # Dry-run completion
            try:
                result = llm.create_completion(prompt="test", max_tokens=5)
                check("LLM dry-run completion", result is not None and len(result) > 0)
            except Exception as e:
                check(f"LLM dry-run", False, "CRITICAL")
                logger.error(f"LLM dry-run failed: {e}")
                critical_failures += 1

    except LLMNotLoadedError:
        check("LLM loaded", False, "CRITICAL")
        critical_failures += 1
    except Exception as e:
        check(f"LLM check", False, "CRITICAL")
        logger.error(f"LLM check failed: {e}")
        critical_failures += 1

    # 6. SECRETS CHECK
    print(f"\n{GREEN}[SECRETS]{RESET}")

    secret_key_set = bool(settings.secret_key) and settings.secret_key not in ["", "changeme", "your-secret-key"]
    check(f"SECRET_KEY set and non-default", secret_key_set)
    if not secret_key_set:
        critical_failures += 1

    pat_key_set = bool(settings.pat_encryption_key) and settings.pat_encryption_key not in ["", "changeme"]
    check(f"PAT_ENCRYPTION_KEY set and non-default", pat_key_set)
    if not pat_key_set:
        critical_failures += 1

    # 7. OPTIONAL CHECKS (WARNINGS)
    print(f"\n{GREEN}[OPTIONAL SETTINGS]{RESET}")

    jira_url_set = bool(settings.jira_url)
    check(f"JIRA_URL configured", jira_url_set, "WARNING" if not jira_url_set else "INFO")

    # SUMMARY
    print(f"\n{GREEN}{'='*60}{RESET}")
    failed_checks = [c for c in checks if c[0] == "FAIL"]
    warn_checks = [c for c in checks if c[0] == "WARN"]

    if failed_checks:
        print(f"{RED}VERIFICATION FAILED{RESET}")
        print(f"Critical failures: {len(failed_checks)}")
        for _, name in failed_checks:
            print(f"  - {name}")
        if warn_checks:
            print(f"Warnings: {len(warn_checks)}")
    elif warn_checks:
        print(f"{YELLOW}VERIFICATION PASSED WITH WARNINGS{RESET}")
        print(f"Warnings: {len(warn_checks)}")
        for _, name in warn_checks:
            print(f"  - {name}")
    else:
        print(f"{GREEN}VERIFICATION PASSED{RESET}")
        print(f"All {len(checks)} checks passed successfully.")

    print(f"{GREEN}{'='*60}{RESET}\n")

    # Exit code
    if critical_failures > 0:
        print(f"{RED}Setup verification FAILED{RESET}")
        sys.exit(1)
    else:
        print(f"{GREEN}Setup verification PASSED{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
