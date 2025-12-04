"""
Adheres to project-instructions.md: domain models under app/core.
"""
"""Request models for the API payloads."""

from pydantic import BaseModel


class AskRequest(BaseModel):
    """Single field request: the question to answer from the chapter."""
    question: str
