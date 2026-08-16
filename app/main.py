from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .agents.citation_agent import CitationMapperAgent
from .agents.research_agent import ResearchAgent
from .agents.summary_agent import SummaryAgent
from .database import initialize_database, save_research_run
from .models import ResearchRequest, ResearchResponse

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Auto-Research AI",
    description=(
        "Multi-agent system for automated research, "
        "paper summarization, and citation mapping."
    ),
    version="0.1.0",
)

research_agent = ResearchAgent()
summary_agent = SummaryAgent()
citation_agent = CitationMapperAgent()


@app.on_event("startup")
async def startup_event() -> None:
    initialize_database()


@app.get("/")
async def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "auto-research-ai",
    }


@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    topic = request.topic.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty.",
        )

    try:
        papers = await research_agent.run(
            topic,
            request.max_papers,
        )

        summaries = await summary_agent.run(papers)

        citation_map = citation_agent.run(papers)

        result = ResearchResponse(
            topic=topic,
            papers=papers,
            summaries=summaries,
            citation_map=citation_map,
        )

        save_research_run(
            topic,
            result.model_dump(),
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Research pipeline failed: {exc}",
        ) from exc