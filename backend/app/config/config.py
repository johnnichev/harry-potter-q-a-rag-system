"""
Constants are used to keep setup simple and deterministic.
"""
from pathlib import Path

# Repository paths
PROJECT_ROOT = Path.cwd()
CHAPTER_FILENAME = "harry-potter-the-philosophers-stone-chapter-1.txt"
CHAPTER_PATH = PROJECT_ROOT / CHAPTER_FILENAME

# Ollama and model settings
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
EMBED_MODEL = "all-minilm"
LLM_MODEL = "llama3.1:8b"

# RAG pipeline settings
CHUNK_SIZE = 250  # words per chunk
CHUNK_OVERLAP = 50  # overlapping words
TOP_K = 4  # retrieved chunks
MAX_TOKENS = 512  # generation budget
MAX_CONTEXT_CHARS = 8000  # prompt context budget

# Dev CORS origins
CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
