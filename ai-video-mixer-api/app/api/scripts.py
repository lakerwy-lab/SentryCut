"""Script planning API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import PlanRequest, PlanResponse
from app.services.planner_service import plan_script

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.post("/plan", response_model=PlanResponse)
def plan(req: PlanRequest):
    try:
        return {"segments": plan_script(req.script)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
