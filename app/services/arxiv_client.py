import re
import xml.etree.ElementTree as ET
from typing import List

import httpx

from ..models import Paper


OPENALEX_API = "https://api.openalex.org/works"
ARXIV_API = "https://export.arxiv.org/api/query"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _rebuild_abstract(inverted_index: dict | None) -> str:
    """Convert OpenAlex inverted-index abstract into normal text."""
    if not inverted_index:
        return ""

    words = []

    for word, positions in inverted_index.items():
        for position in positions:
            words.append((position, word))

    words.sort(key=lambda item: item[0])

    return " ".join(word for _, word in words)


async def _search_openalex(
    topic: str,
    max_results: int = 5,
) -> List[Paper]:
    """Primary academic search using OpenAlex."""

    params = {
        "search": topic,
        "per-page": min(max_results, 10),
        "mailto": "autoresearch@example.com",
    }

    headers = {
        "User-Agent": "AutoResearchAI/1.0",
    }

    timeout = httpx.Timeout(15.0, connect=5.0)

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers=headers,
    ) as client:

        response = await client.get(
            OPENALEX_API,
            params=params,
        )

        response.raise_for_status()

        data = response.json()

    papers: List[Paper] = []

    for item in data.get("results", []):
        title = _clean_text(
            item.get("display_name", "")
        )

        abstract = _rebuild_abstract(
            item.get("abstract_inverted_index")
        )

        authors = []

        for author in item.get("authorships", []):
            author_name = (
                author.get("author", {}).get("display_name", "")
            )

            if author_name:
                authors.append(
                    _clean_text(author_name)
                )

        url = item.get("doi") or item.get("id") or ""

        published = item.get("publication_date")

        if title:
            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    abstract=abstract
                    or "Abstract not available.",
                    url=url,
                    published=published,
                )
            )

    return papers


async def _search_arxiv(
    topic: str,
    max_results: int = 5,
) -> List[Paper]:
    """Secondary fallback search using arXiv."""

    params = {
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": min(max_results, 5),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    headers = {
        "User-Agent": "AutoResearchAI/1.0",
        "Accept": "application/atom+xml",
    }

    timeout = httpx.Timeout(15.0, connect=5.0)

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers=headers,
    ) as client:

        response = await client.get(
            ARXIV_API,
            params=params,
        )

        if response.status_code == 429:
            raise RuntimeError(
                "arXiv is currently rate-limiting requests."
            )

        response.raise_for_status()

    root = ET.fromstring(response.text)

    namespace = {
        "atom": "http://www.w3.org/2005/Atom"
    }

    papers: List[Paper] = []

    for entry in root.findall(
        "atom:entry",
        namespace,
    ):

        title = _clean_text(
            entry.findtext(
                "atom:title",
                default="",
                namespaces=namespace,
            )
        )

        abstract = _clean_text(
            entry.findtext(
                "atom:summary",
                default="",
                namespaces=namespace,
            )
        )

        published = entry.findtext(
            "atom:published",
            default=None,
            namespaces=namespace,
        )

        authors = []

        for author in entry.findall(
            "atom:author",
            namespace,
        ):
            name = _clean_text(
                author.findtext(
                    "atom:name",
                    default="",
                    namespaces=namespace,
                )
            )

            if name:
                authors.append(name)

        url = ""

        for link in entry.findall(
            "atom:link",
            namespace,
        ):
            href = link.attrib.get(
                "href",
                "",
            )

            if link.attrib.get("rel") == "alternate":
                url = href
                break

        if title:
            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    abstract=abstract
                    or "Abstract not available.",
                    url=url,
                    published=published,
                )
            )

    return papers


async def search_arxiv(
    topic: str,
    max_results: int = 5,
) -> List[Paper]:
    """
    Search academic papers.

    OpenAlex is used first because it is more reliable
    for repeated development/testing requests.

    arXiv is used as a fallback.
    """

    topic = _clean_text(topic)

    if not topic:
        return []

    try:
        papers = await _search_openalex(
            topic,
            max_results,
        )

        if papers:
            return papers

    except Exception:
        pass

    try:
        return await _search_arxiv(
            topic,
            max_results,
        )

    except Exception:
        return []