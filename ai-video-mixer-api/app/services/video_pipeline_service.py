"""One-click render pipeline orchestration."""

from __future__ import annotations

from app.db.database import execute
from app.models.schemas import RenderRequest, Segment
from app.services.planner_service import plan_script
from app.services.render_service import render_final_video
from app.services.sentry_search_service import indexed_source_files, match_segments
from app.services.subtitle_service import generate_subtitle
from app.services.task_service import now_iso, update_task
from app.services.tts_service import generate_segment_tts


def _has_matched_source(segment: Segment) -> bool:
    return bool(segment.source_file) and segment.source_start_time is not None


def _normalize_source_paths(segments: list[Segment]) -> list[Segment]:
    from pathlib import Path

    from app.config import settings

    materials_root = settings.materials_dir.resolve()
    allowed_sources = indexed_source_files()
    for segment in segments:
        if not segment.source_file:
            continue
        source_path = Path(segment.source_file)
        if not source_path.is_absolute():
            source_path = settings.base_dir / source_path
        resolved = source_path.resolve()
        is_material = resolved.is_relative_to(materials_root)
        is_indexed = str(resolved) in allowed_sources
        if not is_material and not is_indexed:
            raise ValueError(
                f"Segment {segment.index} source_file is not an indexed material: {segment.source_file}"
            )
        segment.source_file = str(resolved)
    return segments


def _save_segments(task_id: str, segments: list[Segment]) -> None:
    execute("DELETE FROM render_segments WHERE task_id = ?", (task_id,))
    for segment in segments:
        execute(
            """
            INSERT INTO render_segments
              (id, task_id, segment_index, narration, visual_query,
               estimated_duration, actual_duration, source_file,
               source_start_time, source_end_time, similarity_score,
               matched_clip, clip_path, voice_path, subtitle_start,
               subtitle_end, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"{task_id}_seg_{segment.index:03d}",
                task_id,
                segment.index,
                segment.narration,
                segment.visual_query,
                segment.estimated_duration,
                segment.actual_duration,
                segment.source_file,
                segment.source_start_time,
                segment.source_end_time,
                segment.similarity_score,
                segment.matched_clip,
                segment.clip_path,
                segment.voice_path,
                segment.subtitle_start,
                segment.subtitle_end,
                now_iso(),
            ),
        )


def run_render_pipeline(task_id: str, req: RenderRequest) -> None:
    try:
        if req.segments:
            segments = _normalize_source_paths(req.segments)
        else:
            update_task(task_id, "planning", 10, "正在生成分镜")
            segments = plan_script(req.script)

        if all(_has_matched_source(segment) for segment in segments):
            update_task(task_id, "matching", 30, "使用已选择的素材片段")
        else:
            update_task(task_id, "matching", 30, "正在匹配素材")
            segments = match_segments(segments)
        _save_segments(task_id, segments)

        update_task(task_id, "tts_generating", 50, "正在生成口播")
        segments = generate_segment_tts(task_id, segments, req.voice)
        _save_segments(task_id, segments)

        update_task(task_id, "subtitle_generating", 65, "正在生成字幕")
        subtitle_path = generate_subtitle(task_id, segments)
        _save_segments(task_id, segments)

        update_task(task_id, "rendering", 80, "正在合成视频")
        result = render_final_video(task_id, segments, subtitle_path, req.aspect_ratio)
        _save_segments(task_id, segments)

        update_task(
            task_id,
            "completed",
            100,
            "生成完成",
            result_json={
                **result,
                "segments": [segment.model_dump() for segment in segments],
            },
        )
    except Exception as exc:
        update_task(task_id, "failed", 100, "生成失败", error_message=str(exc))
