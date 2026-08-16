import re
from typing import List

from ..config import settings
from ..models import Paper


def extractive_summary(text: str, sentence_count: int = 3) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    return " ".join(sentences[:sentence_count])


class SummaryAgent:
    name = "summary_agent"

    async def run(self, papers: List[Paper]) -> List[str]:
        if not papers:
            return []

        # If no OpenAI API key is configured, use a local
        # extractive summarizer so the project still works.
        if not settings.openai_api_key:
            return [
                extractive_summary(paper.abstract)
                for paper in papers
            ]

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                api_key=settings.openai_api_key
            )

            summaries: List[str] = []

            for paper in papers:
                prompt = (
                    "Summarize this research abstract in 3 concise sentences. "
                    "Mention the problem, approach, and key contribution. "
                    "Do not invent facts.\n\n"
                    f"Title: {paper.title}\n"
                    f"Abstract: {paper.abstract}"
                )

                response = await client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a careful academic "
                                "research assistant."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=0.2,
                )

                content = response.choices[0].message.content or ""
                summaries.append(content.strip())

            return summaries

        except Exception:
            # Fall back to local summarization if the API call fails.
            return [
                extractive_summary(paper.abstract)
                for paper in papers
            ]