"""Task API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import TaskOut
from app.services.task_service import get_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskOut)
def task_detail(task_id: str):
    try:
        return get_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
