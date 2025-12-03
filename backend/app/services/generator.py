import ollama
from ..config import LLM_MODEL, OLLAMA_BASE_URL, MAX_TOKENS


def _client() -> ollama.Client:
    return ollama.Client(host=OLLAMA_BASE_URL)


def build_prompt(question: str, contexts: list[str]) -> str:
    header = "Answer the question concisely using only the provided context. If the context is insufficient, say you cannot answer from the chapter.\n\n"
    ctx = "\n\n".join([f"Context {i+1}:\n{c}" for i, c in enumerate(contexts)])
    return f"{header}{ctx}\n\nQuestion:\n{question}\n\nAnswer:"


def generate_answer(question: str, contexts: list[str]) -> str:
    client = _client()
    prompt = build_prompt(question, contexts)
    res = client.generate(model=LLM_MODEL, prompt=prompt, options={"num_predict": MAX_TOKENS})
    return res["response"].strip()


def stream_answer(question: str, contexts: list[str]):
    client = _client()
    prompt = build_prompt(question, contexts)
    stream = client.generate(model=LLM_MODEL, prompt=prompt, stream=True, options={"num_predict": MAX_TOKENS})
    for s in stream:
        yield s.get("response", "")
