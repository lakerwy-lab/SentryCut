"""SQLite access helpers."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from app.config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS materials (
  id TEXT PRIMARY KEY,
  original_filename TEXT NOT NULL,
  stored_filename TEXT NOT NULL,
  path TEXT NOT NULL,
  duration REAL,
  width INTEGER,
  height INTEGER,
  fps REAL,
  status TEXT DEFAULT 'uploaded',
  embedding_backend TEXT,
  embedding_model TEXT,
  index_error TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  status TEXT DEFAULT 'pending',
  type TEXT NOT NULL,
  progress INTEGER DEFAULT 0,
  current_step TEXT,
  error_message TEXT,
  result_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  completed_at TEXT
);

CREATE TABLE IF NOT EXISTS render_segments (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  segment_index INTEGER NOT NULL,
  narration TEXT NOT NULL,
  visual_query TEXT NOT NULL,
  estimated_duration REAL,
  actual_duration REAL,
  source_file TEXT,
  source_start_time REAL,
  source_end_time REAL,
  similarity_score REAL,
  matched_clip TEXT,
  clip_path TEXT,
  voice_path TEXT,
  subtitle_start REAL,
  subtitle_end REAL,
  created_at TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def fetch_all(sql: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()
    return [dict(row) for row in rows]


def fetch_one(sql: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(sql, tuple(params)).fetchone()
    return dict(row) if row else None


def execute(sql: str, params: Iterable[Any] = ()) -> None:
    with get_connection() as conn:
        conn.execute(sql, tuple(params))
        conn.commit()


def execute_many(sql: str, params: Iterable[Iterable[Any]]) -> None:
    with get_connection() as conn:
        conn.executemany(sql, params)
        conn.commit()
