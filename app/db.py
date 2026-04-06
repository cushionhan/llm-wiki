from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app.config import settings


def initialize_database() -> None:
    with sqlite3.connect(settings.db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                source_type TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                description TEXT,
                source_url TEXT,
                tags_json TEXT NOT NULL,
                raw_path TEXT NOT NULL,
                wiki_path TEXT NOT NULL,
                asset_path TEXT,
                body_text TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                detail TEXT,
                FOREIGN KEY(source_id) REFERENCES sources(id)
            )
            """
        )
        ensure_column(connection, "sources", "body_text", "TEXT")
        ensure_column(connection, "jobs", "started_at", "TEXT")
        connection.commit()


def ensure_column(connection: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
    columns = {
        row[1]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    if column_name in columns:
        return

    connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(settings.db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
