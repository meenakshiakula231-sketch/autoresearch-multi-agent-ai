import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from .config import settings


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS research_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                created_at TEXT NOT NULL,
                result_json TEXT NOT NULL
            )
            """
        )
        connection.commit()


def save_research_run(topic: str, result: Any) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO research_runs (topic, created_at, result_json)
            VALUES (?, ?, ?)
            """,
            (
                topic,
                datetime.now(timezone.utc).isoformat(),
                json.dumps(result),
            ),
        )
        connection.commit()