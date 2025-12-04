"""LLM prompt building and streaming generation using Ollama Chat API."""

import ollama
import logging
from ..config import LLM_MODEL, OLLAMA_BASE_URL, MAX_TOKENS, MAX_CONTEXT_CHARS


def _client() -> ollama.Client:
    return ollama.Client(host=OLLAMA_BASE_URL)


def build_messages(question: str, contexts: list[str]) -> list[dict[str, str]]:
    system_content = (
        "You are answering strictly from the provided context. "
        "Answer succinctly. Do not reference context numbers. "
        "If the context is insufficient, respond: 'I cannot answer from the chapter.'"
    )
    user_contexts = assemble_contexts(contexts, MAX_CONTEXT_CHARS)
    user_content = f"{user_contexts}\n\nQuestion:\n{question}\n\nAnswer:"
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]


def assemble_contexts(contexts: list[str], budget: int) -> str:
    """Join contexts into a single section within the provided char budget.

    Truncates the last context if necessary to fit the budget, and returns
    the final concatenated string.
    """
    segments: list[str] = []
    usedChars = 0
    for context in contexts:
        contextBlock = f"Context:\n{context}"
        nextSize = usedChars + len(contextBlock)
        if nextSize > budget:
            remaining = budget - usedChars
            if remaining > 0:
                segments.append(contextBlock[:remaining])
                usedChars += remaining
            break
        segments.append(contextBlock)
        usedChars += len(contextBlock)
    return "\n\n".join(segments)

def stream_answer(question: str, contexts: list[str]):
    client = _client()
    messages = build_messages(question, contexts)
    logger = logging.getLogger("rag")
    logger.info("Gen(stream): model=%s ctx=%d", LLM_MODEL, len(contexts))
    try:
        stream = client.chat(
            model=LLM_MODEL,
            messages=messages,
            stream=True,
            options={"num_predict": MAX_TOKENS, "temperature": 0, "seed": 1},
        )
        for event in stream:
            yield event.get("message", {}).get("content", "")
    except Exception as exc:
        logger.error("Gen(stream) failed: %s", exc)
        raise
