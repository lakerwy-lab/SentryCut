"""Segment-level TTS generation."""

from __future__ import annotations

import asyncio
from pathlib import Path

import edge_tts

from app.config import settings
from app.models.schemas import Segment
from app.services.media_service import ffmpeg_exe, media_duration, run_ffmpeg


async def _save_edge_tts(text: str, voice: str, output_path: Path) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))


def _normalize_audio(input_path: Path, output_path: Path) -> None:
    run_ffmpeg(
        [
            ffmpeg_exe(),
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-ar",
            "44100",
            "-ac",
            "2",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            str(output_path),
        ]
    )


def _generate_silent_audio(output_path: Path, duration: float) -> None:
    run_ffmpeg(
        [
            ffmpeg_exe(),
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=stereo",
            "-t",
            str(max(0.5, duration)),
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            str(output_path),
        ]
    )


def generate_segment_tts(task_id: str, segments: list[Segment], voice: str) -> list[Segment]:
    task_voice_dir = settings.voice_dir / task_id
    task_voice_dir.mkdir(parents=True, exist_ok=True)

    for segment in segments:
        raw_path = task_voice_dir / f"seg_{segment.index:03d}_raw.mp3"
        voice_path = task_voice_dir / f"seg_{segment.index:03d}.m4a"
        try:
            asyncio.run(_save_edge_tts(segment.narration, voice, raw_path))
            _normalize_audio(raw_path, voice_path)
            raw_path.unlink(missing_ok=True)
        except Exception:
            if not settings.allow_silent_tts_fallback:
                raise
            fallback_duration = segment.estimated_duration or max(2.0, len(segment.narration) / 4.5)
            _generate_silent_audio(voice_path, fallback_duration)

        segment.voice_path = voice_path.relative_to(settings.base_dir).as_posix()
        segment.actual_duration = round(media_duration(voice_path), 3)

    return segments
