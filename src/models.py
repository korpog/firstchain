from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.documents import Document


class Question(BaseModel):
    question: str = Field(..., min_length=10, max_length=200)


class Answer(BaseModel):
    question: str
    context: List[Document]
    answer: str
