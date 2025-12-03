import ollama
from ..config import OLLAMA_BASE_URL, EMBED_MODEL, LLM_MODEL


def check_models() -> bool:
    client = ollama.Client(host=OLLAMA_BASE_URL)
    try:
        client.embeddings(model=EMBED_MODEL, input="test")
        client.generate(model=LLM_MODEL, prompt="ok")
        return True
    except Exception:
        return False
