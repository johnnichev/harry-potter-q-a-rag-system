from typing import Optional
from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    stream: Optional[bool] = None
    include_sources: Optional[bool] = None
    format: Optional[str] = None  # 'json' | 'text'


class AskMetaResponse(BaseModel):
    answer: str
    sources: list
