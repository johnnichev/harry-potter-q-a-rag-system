"""LLM prompt building and streaming generation.

Streaming is the primary mechanism for answering; tokens are emitted as they
arrive from the model to improve perceived latency.
"""

import ollama
import logging
from ..config import LLM_MODEL, OLLAMA_BASE_URL, MAX_TOKENS, MAX_CONTEXT_CHARS


def _client() -> ollama.Client:
    """Create a pre-configured Ollama client bound to the local host."""
    return ollama.Client(host=OLLAMA_BASE_URL)


def build_prompt(question: str, contexts: list[str]) -> str:
    """Construct a compact prompt from retrieved contexts and the question.

    Contexts are concatenated with a small header and trimmed to fit the
    character budget used by the model to keep responses stable.
    """
    header = (
        "You are answering strictly from the provided context. "
        "Answer succinctly. Do not reference context numbers or say 'From Context'. "
        "If the context is insufficient, respond: 'I cannot answer from the chapter.'\n\n"
    )

    contextSection = assemble_contexts(contexts, MAX_CONTEXT_CHARS)
    return f"{header}{contextSection}\n\nQuestion:\n{question}\n\nAnswer:"


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
    """Yield response tokens from the model for the given question and contexts."""
    client = _client()
    prompt = build_prompt(question, contexts)
    logger = logging.getLogger("rag")
    logger.info("Gen(stream): model=%s ctx=%d prompt_len=%d", LLM_MODEL, len(contexts), len(prompt))
    try:
        stream = client.generate(
            model=LLM_MODEL,
            prompt=prompt,
            stream=True,
            options={"num_predict": MAX_TOKENS, "temperature": 0, "seed": 1},
        )
        for event in stream:
            yield event.get("response", "")
    except Exception as exc:
        logger.error("Gen(stream) failed: %s", exc)
        raise
