from backend.app.services.chunker import chunk_text


def test_chunker_basic():
    text = "one two three four five six seven eight nine ten"
    chunks = chunk_text(text, 4, 1)
    assert len(chunks) >= 3
    assert all(isinstance(c, str) and len(c) > 0 for c in chunks)

