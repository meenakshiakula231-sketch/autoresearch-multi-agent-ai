import re
from collections import defaultdict
from typing import Dict, List

from ..models import Paper


class CitationMapperAgent:
    name = "citation_mapper_agent"

    def run(self, papers: List[Paper]) -> Dict[str, List[str]]:
        """
        Build an initial relationship map between discovered papers.

        This MVP uses title-keyword overlap. Later, this can be replaced
        with real citation metadata from services such as OpenAlex,
        Crossref, or Semantic Scholar.
        """
        mapping: Dict[str, List[str]] = defaultdict(list)

        normalized = {
            paper.title: self._keywords(paper.title)
            for paper in papers
        }

        for source in papers:
            for target in papers:
                if source.title == target.title:
                    continue

                overlap = (
                    normalized[source.title]
                    & normalized[target.title]
                )

                if len(overlap) >= 2:
                    mapping[source.title].append(target.title)

        return dict(mapping)

    @staticmethod
    def _keywords(title: str) -> set:
        words = re.findall(
            r"[a-zA-Z0-9]+",
            title.lower(),
        )

        stop_words = {
            "the",
            "a",
            "an",
            "of",
            "for",
            "and",
            "to",
            "in",
            "on",
            "with",
            "from",
            "using",
            "via",
        }

        return {
            word
            for word in words
            if len(word) > 3 and word not in stop_words
        }