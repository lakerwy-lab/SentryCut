"""Material API routes."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.models.schemas import IndexRequest, MaterialListOut, MaterialOut, TaskCreated
from app.services.material_service import delete_material, get_materials, list_materials, save_upload
from app.services.sentry_search_service import index_materials
from app.services.task_service import create_task

router = APIRouter(prefix="/materials", tags=["materials"])


@router.post("/upload", response_model=MaterialOut)
async def upload_material(file: UploadFile = File(...)):
    try:
        return await save_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("", response_model=MaterialListOut)
def materials():
    return {"items": list_materials()}


@router.delete("/{material_id}")
def delete_material_route(material_id: str):
    try:
        return delete_material(material_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/index", response_model=TaskCreated)
def index_materials_route(req: IndexRequest, background_tasks: BackgroundTasks):
    selected = req.material_ids or [m["id"] for m in get_materials()]
    if not selected:
        raise HTTPException(status_code=400, detail="No materials to index.")
    task = create_task("index", "等待建立素材索引")
    background_tasks.add_task(index_materials, task["task_id"], selected)
    return {"task_id": task["task_id"], "type": "index", "status": task["status"]}
