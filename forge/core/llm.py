import logging
from pathlib import Path
from llama_cpp import Llama

from forge.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMNotLoadedError(Exception):
    pass


_llm_instance = None


def get_llm():
    global _llm_instance
    if _llm_instance is None:
        settings = get_settings()
        path = Path(settings.llm_model_path)
        if not path.exists():
            raise LLMNotLoadedError(
                f"LLM model not found at: {path}\n"
                f"Update LLM_MODEL_PATH in .env and restart the server."
            )
        logger.info(f"Loading LLM from {path}")
        _llm_instance = Llama(
            model_path=str(path),
            n_gpu_layers=settings.llm_gpu_layers,
            n_ctx=settings.llm_context_size,
            n_threads=settings.llm_threads,
            verbose=False
        )
        logger.info("LLM loaded successfully")
    return _llm_instance


def llm_complete(prompt: str, system: str = "", max_tokens: int = 2048) -> str:
    llm = get_llm()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = llm.create_chat_completion(messages=messages, max_tokens=max_tokens)
    return response["choices"][0]["message"]["content"]
