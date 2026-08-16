from typing import List

from ..models import Paper
from ..services.arxiv_client import search_arxiv


class ResearchAgent:
    name = "research_agent"

    async def run(self, topic: str, max_papers: int) -> List[Paper]:
        return await search_arxiv(topic, max_papers)