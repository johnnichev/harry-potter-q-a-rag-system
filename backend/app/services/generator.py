import ollama
import logging
from ..config import LLM_MODEL, OLLAMA_BASE_URL, MAX_TOKENS, MAX_CONTEXT_CHARS


def _client() -> ollama.Client:
    return ollama.Client(host=OLLAMA_BASE_URL)


def build_prompt(question: str, contexts: list[str]) -> str:
    header = (
        "You are answering strictly from the provided context. "
        "Answer succinctly. Do not reference context numbers or say 'From Context'. "
        "If the context is insufficient, respond: 'I cannot answer from the chapter.'\n\n"
    )
    # Assemble contexts and enforce a character budget for stability
    joined = []
    used = 0
    for c in contexts:
        cstr = f"Context:\n{c}"
        if used + len(cstr) > MAX_CONTEXT_CHARS:
            # truncate remainder to fit budget
            remaining = MAX_CONTEXT_CHARS - used
            if remaining > 0:
                joined.append(cstr[:remaining])
                used += remaining
            break
        joined.append(cstr)
        used += len(cstr)
    ctx = "\n\n".join(joined)
    return f"{header}{ctx}\n\nQuestion:\n{question}\n\nAnswer:"


def generate_answer(question: str, contexts: list[str]) -> str:
    client = _client()
    prompt = build_prompt(question, contexts)
    logger = logging.getLogger("rag")
    logger.info("Gen: model=%s ctx=%d prompt_len=%d", LLM_MODEL, len(contexts), len(prompt))
    res = client.generate(
        model=LLM_MODEL,
        prompt=prompt,
        options={"num_predict": MAX_TOKENS, "temperature": 0, "seed": 1},
    )
    logger.info("Gen: completed response_len=%d", len(res.get("response", "")))
    return res["response"].strip()


def stream_answer(question: str, contexts: list[str]):
    client = _client()
    prompt = build_prompt(question, contexts)
    logger = logging.getLogger("rag")
    logger.info("Gen(stream): model=%s ctx=%d prompt_len=%d", LLM_MODEL, len(contexts), len(prompt))
    stream = client.generate(
        model=LLM_MODEL,
        prompt=prompt,
        stream=True,
        options={"num_predict": MAX_TOKENS, "temperature": 0, "seed": 1},
    )
    for s in stream:
        yield s.get("response", "")
