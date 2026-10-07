# Auto-Research AI — Base44 Dev Environment

## What this app is

A FastAPI app ("Auto-Research AI") that serves a static glassmorphic dashboard
(`static/index.html`) at `/` and exposes `POST /api/research` to search academic
papers (OpenAlex primary, arXiv fallback), summarize them, and build citation
maps. Results are stored in a local SQLite database.

## Running it

```bash
docker compose -f docker-compose.base44.yml up -d --build
```

- Web entry point: http://localhost:3000
- Health check: http://localhost:3000/health
- API: `POST /api/research` with JSON body `{"topic": "...", "max_papers": 5}`

## Key details

- **Single service**: FastAPI + Uvicorn with `--reload` (hot reload via bind mount).
- **Database**: SQLite at `/data/research.db` (Docker volume `app_data`).
- **Missing deps fixed**: `httpx` and `python-dotenv` were used in code but absent
  from `requirements.txt` — they have been added.
- **OpenAI API key is optional**: `OPENAI_API_KEY` in env. Without it, the
  SummarizerAgent falls back to a local extractive (regex-based) summarizer. The
  app boots and works fully without any external credentials.
- **External APIs**: OpenAlex and arXiv are free public APIs — no key needed.
  If both are unreachable, the research endpoint returns an empty paper list
  (graceful degradation).
- **nltk** is listed in requirements.txt but not actually imported by the code;
  the summarizer uses a custom regex-based extractive approach.

## Verifying it works

1. `curl http://localhost:3000/health` → `{"status":"ok",...}`
2. `curl http://localhost:3000/` → returns the HTML dashboard
3. `curl -X POST http://localhost:3000/api/research -H 'Content-Type: application/json' -d '{"topic":"transformers","max_papers":3}'` → returns papers + summaries
