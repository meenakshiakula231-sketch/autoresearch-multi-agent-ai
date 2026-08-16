import asyncio
import re
import xml.etree.ElementTree as ET
from typing import List

import httpx

from ..models import Paper


ARXIV_API = "https://export.arxiv.org/api/query"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


async def search_arxiv(topic: str, max_results: int = 5) -> List[Paper]:
    params = {
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    headers = {
        "User-Agent": (
            "AutoResearchAI/1.0 "
            "(academic research project; contact: admin@example.com)"
        ),
        "Accept": "application/atom+xml",
    }

    timeout = httpx.Timeout(30.0, connect=10.0)

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers=headers,
    ) as client:

        for attempt in range(3):
            try:
                response = await client.get(
                    ARXIV_API,
                    params=params,
                )

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")

                    try:
                        wait_time = int(retry_after) if retry_after else 5
                    except ValueError:
                        wait_time = 5

                    wait_time = min(max(wait_time, 5), 30)

                    if attempt < 2:
                        await asyncio.sleep(wait_time)
                        continue

                    raise RuntimeError(
                        "arXiv is temporarily rate-limiting requests. "
                        "Please wait a little and try the research again."
                    )

                response.raise_for_status()
                break

            except httpx.RequestError as exc:
                if attempt < 2:
                    await asyncio.sleep(3 * (attempt + 1))
                    continue

                raise RuntimeError(
                    f"Unable to connect to arXiv: {exc}"
                ) from exc

        else:
            raise RuntimeError("Unable to retrieve papers from arXiv.")

    root = ET.fromstring(response.text)

    namespace = {
        "atom": "http://www.w3.org/2005/Atom"
    }

    papers: List[Paper] = []

    for entry in root.findall("atom:entry", namespace):
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

        authors = [
            _clean_text(
                author.findtext(
                    "atom:name",
                    default="",
                    namespaces=namespace,
                )
            )
            for author in entry.findall(
                "atom:author",
                namespace,
            )
        ]

        url = ""

        for link in entry.findall("atom:link", namespace):
            href = link.attrib.get("href", "")

            if link.attrib.get("rel") == "alternate":
                url = href
                break

        if title and abstract:
            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    url=url,
                    published=published,
                )
            )

    return papers