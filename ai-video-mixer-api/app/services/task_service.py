"""Task persistence helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from app.db.database import execute, fetch_one


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_task(task_type: str, current_step: str = "等待处理") -> dict:
    task_id = f"{task_type}_{uuid4().hex[:12]}"
    now = now_iso()
    execute(
        """
        INSERT INTO tasks
          (id, type, status, progress, current_step, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (task_id, task_type, "pending", 0, current_step, now, now),
    )
    return get_task(task_id)


def update_task(
    task_id: str,
    status: str,
    progress: int,
    current_step: str,
    *,
    result_json: dict | None = None,
    error_message: str | None = None,
) -> None:
    completed_at = now_iso() if status in {"completed", "failed"} else None
    execute(
        """
        UPDATE tasks
        SET status = ?,
            progress = ?,
            current_step = ?,
            result_json = COALESCE(?, result_json),
            error_message = ?,
            updated_at = ?,
            completed_at = COALESCE(?, completed_at)
        WHERE id = ?
        """,
        (
            status,
            max(0, min(100, progress)),
            current_step,
            json.dumps(result_json, ensure_ascii=False) if result_json is not None else None,
            error_message,
            now_iso(),
            completed_at,
            task_id,
        ),
    )


def get_task(task_id: str) -> dict:
    row = fetch_one("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if not row:
        raise KeyError(f"Task not found: {task_id}")
    result = json.loads(row["result_json"]) if row.get("result_json") else None
    return {
        "task_id": row["id"],
        "type": row["type"],
        "status": row["status"],
        "progress": row["progress"],
        "current_step": row["current_step"],
        "output_url": result.get("output_url") if isinstance(result, dict) else None,
        "subtitle_url": result.get("subtitle_url") if isinstance(result, dict) else None,
        "error_message": row["error_message"],
        "result_json": result,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "completed_at": row["completed_at"],
    }
