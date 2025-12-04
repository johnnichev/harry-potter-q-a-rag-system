import logging
import ollama
from ..config import OLLAMA_BASE_URL, EMBED_MODEL, LLM_MODEL


def check_models() -> bool:
    logger = logging.getLogger("rag")
    client = ollama.Client(host=OLLAMA_BASE_URL)
    logger.info("Preflight: checking Ollama at %s", OLLAMA_BASE_URL)
    try:
        client.embeddings(model=EMBED_MODEL, prompt="test")
        logger.info("Preflight: embeddings model '%s' OK", EMBED_MODEL)
        client.generate(model=LLM_MODEL, prompt="ok")
        logger.info("Preflight: generation model '%s' OK", LLM_MODEL)
        return True
    except Exception as e:
        logger.error("Preflight failed: %s", e)
        return False
