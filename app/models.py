from typing import List, Optional

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=300)
    max_papers: int = Field(default=5, ge=1, le=20)


class Paper(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    url: str
    published: Optional[str] = None
    references: List[str] = []


class ResearchResponse(BaseModel):
    topic: str
    papers: List[Paper]
    summaries: List[str]
    citation_map: dict