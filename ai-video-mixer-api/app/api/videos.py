"""Video matching and rendering API routes."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.models.schemas import MatchRequest, MatchResponse, RenderRequest, TaskCreated
from app.services.sentry_search_service import match_segments
from app.services.task_service import create_task
from app.services.video_pipeline_service import run_render_pipeline

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/match-clips", response_model=MatchResponse)
def match_clips(req: MatchRequest):
    try:
        return {"segments": match_segments(req.segments, results=req.results)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/render", response_model=TaskCreated)
def render(req: RenderRequest, background_tasks: BackgroundTasks):
    task = create_task("render", "等待生成视频")
    background_tasks.add_task(run_render_pipeline, task["task_id"], req)
    return {"task_id": task["task_id"], "type": "render", "status": task["status"]}
