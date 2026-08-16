import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    database_path: str = os.getenv("DATABASE_PATH", "research.db")
    arxiv_max_results: int = int(os.getenv("ARXIV_MAX_RESULTS", "10"))


settings = Settings()