"""
Adheres to project-instructions.md: domain models under app/core.
"""
from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
