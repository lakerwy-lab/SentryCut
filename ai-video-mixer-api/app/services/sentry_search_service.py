"""SentrySearch integration through Python imports."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from app.config import settings
from app.services.material_service import get_materials, update_material_status
from app.services.task_service import update_task
from sentrysearch.chunker import chunk_video, preprocess_chunk
from sentrysearch.embedder import get_embedder, reset_embedder
from sentrysearch.search import search_footage
from sentrysearch.store import SentryStore


def _absolute_material_path(material: dict) -> Path:
    return (settings.base_dir / material["path"]).resolve()


def indexed_source_files() -> set[str]:
    store = SentryStore(db_path=settings.chroma_dir, backend=settings.embedding_backend)
    return {str(Path(path).resolve()) for path in store.get_stats()["source_files"]}


def index_materials(task_id: str, material_ids: list[str]) -> None:
    materials = get_materials(material_ids)
    if not materials:
        update_task(task_id, "failed", 100, "没有可索引的素材", error_message="No materials found.")
        return

    indexed = 0
    failed = 0
    store = SentryStore(db_path=settings.chroma_dir, backend=settings.embedding_backend)

    try:
        update_task(task_id, "indexing", 5, "正在加载 embedding 后端")
        embedder = get_embedder(settings.embedding_backend)
        total = len(materials)

        for file_idx, material in enumerate(materials, 1):
            material_id = material["id"]
            source_path = _absolute_material_path(material)
            chunks = []
            cleanup: list[str] = []
            update_material_status(
                material_id,
                "indexing",
                embedding_backend=settings.embedding_backend,
                embedding_model=settings.embedding_model,
                index_error=None,
            )
            update_task(
                task_id,
                "indexing",
                int(10 + 80 * (file_idx - 1) / max(total, 1)),
                f"正在索引素材 {file_idx}/{total}",
            )

            try:
                chunks = chunk_video(
                    str(source_path),
                    chunk_duration=settings.chunk_duration,
                    overlap=settings.chunk_overlap,
                )
                for chunk_idx, chunk in enumerate(chunks, 1):
                    chunk_id = store.make_chunk_id(str(source_path), chunk["start_time"])
                    cleanup.append(chunk["chunk_path"])
                    if store.has_chunk(chunk_id):
                        continue

                    embed_path = preprocess_chunk(
                        chunk["chunk_path"],
                        target_resolution=settings.target_resolution,
                        target_fps=settings.target_fps,
                    )
                    if embed_path != chunk["chunk_path"]:
                        cleanup.append(embed_path)

                    embedding = embedder.embed_video_chunk(embed_path)
                    store.add_chunk(
                        chunk_id,
                        embedding,
                        {
                            "source_file": str(source_path),
                            "start_time": chunk["start_time"],
                            "end_time": chunk["end_time"],
                            "material_id": material_id,
                        },
                    )

                indexed += 1
                update_material_status(
                    material_id,
                    "indexed",
                    embedding_backend=settings.embedding_backend,
                    embedding_model=settings.embedding_model,
                    index_error=None,
                )
            except Exception as exc:
                failed += 1
                update_material_status(
                    material_id,
                    "failed",
                    embedding_backend=settings.embedding_backend,
                    embedding_model=settings.embedding_model,
                    index_error=str(exc),
                )
            finally:
                for path in cleanup:
                    Path(path).unlink(missing_ok=True)
                if chunks:
                    shutil.rmtree(Path(chunks[0]["chunk_path"]).parent, ignore_errors=True)

        stats = store.get_stats()
        update_task(
            task_id,
            "completed" if failed == 0 else "failed",
            100,
            "素材索引完成" if failed == 0 else "部分素材索引失败",
            result_json={
                "indexed_count": indexed,
                "failed_count": failed,
                "stats": stats,
            },
            error_message=None if failed == 0 else f"{failed} material(s) failed to index.",
        )
    except Exception as exc:
        update_task(task_id, "failed", 100, "素材索引失败", error_message=str(exc))
    finally:
        reset_embedder()


def match_segments(segments, *, results: int = 1):
    store = SentryStore(db_path=settings.chroma_dir, backend=settings.embedding_backend)
    if store.get_stats()["total_chunks"] == 0:
        raise RuntimeError("No indexed footage found. Upload and index materials first.")

    reset_embedder()
    get_embedder(settings.embedding_backend)
    matched = []
    try:
        for segment in segments:
            hits = search_footage(segment.visual_query, store, n_results=max(1, results))
            if not hits:
                raise RuntimeError(f"No clip matched segment {segment.index}: {segment.visual_query}")
            hit = hits[0]
            segment.source_file = hit["source_file"]
            segment.source_start_time = float(hit["start_time"])
            segment.source_end_time = float(hit["end_time"])
            segment.similarity_score = float(hit["similarity_score"])
            matched.append(segment)
        return matched
    finally:
        reset_embedder()
