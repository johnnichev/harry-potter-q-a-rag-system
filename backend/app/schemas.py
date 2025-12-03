from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskMetaResponse(BaseModel):
    answer: str
    sources: list
