def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
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
