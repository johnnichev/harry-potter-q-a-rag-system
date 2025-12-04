"""Chunking utilities.

Splits raw chapter text into overlapping word windows. Small overlaps help
retrieval keep context continuity across boundaries without making chunks too
large for embedding models.
"""

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split ``text`` into word-based chunks.

    - ``chunk_size``: number of words per chunk
    - ``overlap``: words carried over between consecutive chunks

    Returns a list of chunk strings in reading order.
    """
    words = text.split()
    chunks = []
    i = 0
    n = len(words)
    while i < n:
        chunk_words = words[i : min(i + chunk_size, n)]
        chunks.append(" ".join(chunk_words))
        if i + chunk_size >= n:
            break
        i += max(chunk_size - overlap, 1)
    return chunks
