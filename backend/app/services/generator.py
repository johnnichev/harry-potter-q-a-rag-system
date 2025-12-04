import ollama
from ..config import LLM_MODEL, OLLAMA_BASE_URL, MAX_TOKENS


def _client() -> ollama.Client:
    return ollama.Client(host=OLLAMA_BASE_URL)


def build_prompt(question: str, contexts: list[str]) -> str:
    header = (
        "You are answering strictly from the provided context. "
        "Answer succinctly. Do not reference context numbers or say 'From Context'. "
        "If the context is insufficient, respond: 'I cannot answer from the chapter.'\n\n"
    )
    ctx = "\n\n".join([f"Context:\n{c}" for c in contexts])
    return f"{header}{ctx}\n\nQuestion:\n{question}\n\nAnswer:"


def generate_answer(question: str, contexts: list[str]) -> str:
    client = _client()
    prompt = build_prompt(question, contexts)
    res = client.generate(
        model=LLM_MODEL,
        prompt=prompt,
        options={"num_predict": MAX_TOKENS, "temperature": 0, "seed": 1},
    )
    return res["response"].strip()


def stream_answer(question: str, contexts: list[str]):
    client = _client()
    prompt = build_prompt(question, contexts)
    stream = client.generate(
        model=LLM_MODEL,
        prompt=prompt,
        stream=True,
        options={"num_predict": MAX_TOKENS, "temperature": 0},
    )
    for s in stream:
        yield s.get("response", "")
