"""
Adheres to project-instructions.md: configuration isolated under app/config.
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", Path.cwd()))
CHAPTER_FILENAME = os.getenv(
    "CHAPTER_FILENAME",
    "harry-potter-the-philosophers-stone-chapter-1.txt",
)
CHAPTER_PATH = Path(os.getenv("CHAPTER_PATH", PROJECT_ROOT / CHAPTER_FILENAME))

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-minilm")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K = int(os.getenv("TOP_K", "4"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))
MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "8000"))

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
