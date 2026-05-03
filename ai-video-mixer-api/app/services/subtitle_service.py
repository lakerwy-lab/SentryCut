"""SRT subtitle generation from segment audio durations."""

from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.models.schemas import Segment


def _fmt_srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    hours, rem = divmod(ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_subtitle(task_id: str, segments: list[Segment]) -> Path:
    subtitle_path = settings.subtitles_dir / f"{task_id}.srt"
    cursor = 0.0
    lines: list[str] = []

    for segment in segments:
        duration = segment.actual_duration or segment.estimated_duration or 2.0
        segment.subtitle_start = round(cursor, 3)
        segment.subtitle_end = round(cursor + duration, 3)
        lines.extend(
            [
                str(segment.index),
                f"{_fmt_srt_time(segment.subtitle_start)} --> {_fmt_srt_time(segment.subtitle_end)}",
                segment.narration,
                "",
            ]
        )
        cursor += duration

    subtitle_path.write_text("\n".join(lines), encoding="utf-8")
    return subtitle_path
