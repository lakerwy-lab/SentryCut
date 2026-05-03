"""Material storage and listing."""

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import settings
from app.db.database import execute, fetch_all, fetch_one
from app.services.media_service import probe_media
from app.services.task_service import now_iso
from sentrysearch.store import SentryStore


SUPPORTED_EXTENSIONS = {".mp4", ".mov"}


def _public_path(path: Path) -> str:
    return path.relative_to(settings.base_dir).as_posix()


def list_materials() -> list[dict]:
    return fetch_all("SELECT * FROM materials ORDER BY created_at DESC")


def get_material(material_id: str) -> dict | None:
    return fetch_one("SELECT * FROM materials WHERE id = ?", (material_id,))


def get_materials(material_ids: list[str] | None = None) -> list[dict]:
    if material_ids:
        placeholders = ",".join("?" for _ in material_ids)
        return fetch_all(f"SELECT * FROM materials WHERE id IN ({placeholders})", material_ids)
    return fetch_all("SELECT * FROM materials ORDER BY created_at DESC")


def update_material_status(
    material_id: str,
    status: str,
    *,
    embedding_backend: str | None = None,
    embedding_model: str | None = None,
    index_error: str | None = None,
) -> None:
    execute(
        """
        UPDATE materials
        SET status = ?,
            embedding_backend = COALESCE(?, embedding_backend),
            embedding_model = COALESCE(?, embedding_model),
            index_error = ?
        WHERE id = ?
        """,
        (status, embedding_backend, embedding_model, index_error, material_id),
    )


def delete_material(material_id: str) -> dict:
    material = get_material(material_id)
    if not material:
        raise KeyError(f"Material not found: {material_id}")
    if material["status"] == "indexing":
        raise ValueError("Cannot delete a material while it is indexing.")

    source_path = (settings.base_dir / material["path"]).resolve()
    materials_root = settings.materials_dir.resolve()
    if not source_path.is_relative_to(materials_root):
        raise ValueError("Material path is outside the materials directory.")

    backend = material.get("embedding_backend") or settings.embedding_backend
    store = SentryStore(db_path=settings.chroma_dir, backend=backend)
    removed_chunks = store.remove_file(str(source_path))

    source_path.unlink(missing_ok=True)
    execute("DELETE FROM materials WHERE id = ?", (material_id,))
    return {"material_id": material_id, "removed_chunks": removed_chunks}


async def save_upload(file: UploadFile) -> dict:
    original = file.filename or "upload.mp4"
    ext = Path(original).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError("Only .mp4 and .mov files are supported in v1.")

    material_id = f"mat_{uuid4().hex[:12]}"
    stored_filename = f"{material_id}{ext}"
    dest = settings.materials_dir / stored_filename
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            out.write(chunk)

    try:
        meta = probe_media(dest)
    except Exception:
        dest.unlink(missing_ok=True)
        raise

    created_at = now_iso()
    execute(
        """
        INSERT INTO materials
          (id, original_filename, stored_filename, path, duration, width, height,
           fps, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            material_id,
            original,
            stored_filename,
            _public_path(dest),
            meta.get("duration"),
            meta.get("width"),
            meta.get("height"),
            meta.get("fps"),
            "uploaded",
            created_at,
        ),
    )
    return get_material(material_id)
