"""Simple file loader for chapter text."""

from pathlib import Path


def load_text(path: Path) -> str:
    """Read UTF-8 text from ``path`` and return the contents."""
    return path.read_text(encoding="utf-8")
