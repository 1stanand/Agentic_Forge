from pydantic_settings import BaseSettings
from pathlib import Path
from functools import lru_cache


class Settings(BaseSettings):
    # Machine
    machine_profile: str = "dev"

    # Database
    db_name: str = "agentic_forge_local"
    db_user: str = "postgres"
    db_password: str = ""
    db_host: str = "localhost"
    db_port: int = 5432

    # LLM
    llm_backend: str = "llama_cpp"
    llm_model_path: Path = Path("")
    llm_gpu_layers: int = 0
    llm_context_size: int = 8192
    llm_threads: int = 4

    # Models
    embedding_model: str = ""
    cross_encoder_model: str = ""

    # Paths
    features_repo_path: Path = Path("")
    order_json_path: Path = Path("")
    cas_docs_path: Path = Path("")
    faiss_index_dir: Path = Path("")
    log_path: Path = Path("logs/forge.log")

    # Auth
    secret_key: str = ""
    jwt_expire_hours: int = 12
    pat_encryption_key: str = ""

    # JIRA
    jira_url: str = ""
    jira_pat: str = ""

    # Retrieval
    low_match_threshold: float = 0.3
    self_rag_max_retries: int = 1
    critic_max_loops: int = 1

    # Generation Jobs
    max_concurrent_jobs: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
