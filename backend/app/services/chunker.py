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
    # Normalize parameters to avoid accidental negatives/zeros
    size = max(int(chunk_size), 1)
    carry = max(int(overlap), 0)

    words = text.split()
    chunks: list[str] = []
    start_index = 0
    total_words = len(words)

    while start_index < total_words:
        end_index = min(start_index + size, total_words)
        current_slice = words[start_index:end_index]
        chunks.append(" ".join(current_slice))

        # Stop if we reached the end; otherwise advance with overlap
        if end_index >= total_words:
            break
        step = max(size - carry, 1)
        start_index += step

    return chunks
