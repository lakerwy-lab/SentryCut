"""FFmpeg video rendering pipeline."""

from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.models.schemas import Segment
from app.services.media_service import ffmpeg_exe, media_duration, run_ffmpeg, to_static_url


ASPECT_PRESETS = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
}

_VIDEO_ENCODER: str | None = None


def _concat_line(path: Path) -> str:
    escaped = path.resolve().as_posix().replace("'", "'\\''")
    return f"file '{escaped}'"


def _subtitle_filter_path(path: Path) -> str:
    escaped = path.resolve().as_posix().replace("\\", "/").replace(":", r"\:")
    escaped = escaped.replace("'", r"\'")
    return f"subtitles='{escaped}'"


def _encode_video_args(codec: str) -> list[str]:
    if codec == "libx264":
        return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p"]
    return ["-c:v", "mpeg4", "-q:v", "5", "-pix_fmt", "yuv420p"]


def _run_video_encode(base_args: list[str], output_path: Path) -> str:
    global _VIDEO_ENCODER
    preferred = [_VIDEO_ENCODER] if _VIDEO_ENCODER else []
    preferred.extend(codec for codec in ("libx264", "mpeg4") if codec not in preferred)
    last_error: RuntimeError | None = None
    for codec in preferred:
        if codec is None:
            continue
        try:
            run_ffmpeg([*base_args, *_encode_video_args(codec), str(output_path)])
            _VIDEO_ENCODER = codec
            return codec
        except RuntimeError as exc:
            last_error = exc
            if codec == "mpeg4":
                break
    if last_error:
        raise last_error
    raise RuntimeError("No video encoder was available.")


def _transcode_clip(
    source_file: str,
    output_path: Path,
    *,
    start_time: float,
    duration: float,
    width: int,
    height: int,
) -> None:
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},fps=30,format=yuv420p"
    )
    base_args = [
        ffmpeg_exe(),
        "-y",
        "-i",
        source_file,
        "-ss",
        str(max(0.0, start_time)),
        "-t",
        str(max(0.5, duration)),
        "-vf",
        vf,
        "-an",
    ]
    _run_video_encode(base_args, output_path)


def _concat_video(clips: list[Path], output_path: Path) -> None:
    concat_path = output_path.with_name(f"{output_path.stem}_concat.txt")
    concat_path.write_text("\n".join(_concat_line(p) for p in clips), encoding="utf-8")
    run_ffmpeg(
        [
            ffmpeg_exe(),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            str(output_path),
        ],
    )


def _concat_audio(segments: list[Segment], output_path: Path) -> None:
    voice_files = [settings.base_dir / str(s.voice_path) for s in segments if s.voice_path]
    concat_path = output_path.with_name(f"{output_path.stem}_concat.txt")
    concat_path.write_text("\n".join(_concat_line(p) for p in voice_files), encoding="utf-8")
    run_ffmpeg(
        [
            ffmpeg_exe(),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            str(output_path),
        ]
    )


def render_final_video(
    task_id: str,
    segments: list[Segment],
    subtitle_path: Path,
    aspect_ratio: str,
) -> dict:
    width, height = ASPECT_PRESETS[aspect_ratio]
    task_clip_dir = settings.clips_dir / task_id
    task_clip_dir.mkdir(parents=True, exist_ok=True)

    clip_paths: list[Path] = []
    for segment in segments:
        if not segment.source_file or segment.source_start_time is None:
            raise RuntimeError(f"Segment {segment.index} has no matched source clip.")
        duration = segment.actual_duration or segment.estimated_duration or 2.0
        output_clip = task_clip_dir / f"seg_{segment.index:03d}.mp4"
        source_duration = media_duration(segment.source_file)
        start = min(float(segment.source_start_time), max(0.0, source_duration - 0.5))
        duration = min(duration, max(0.5, source_duration - start))
        _transcode_clip(
            segment.source_file,
            output_clip,
            start_time=start,
            duration=duration,
            width=width,
            height=height,
        )
        segment.matched_clip = output_clip.relative_to(settings.base_dir).as_posix()
        segment.clip_path = segment.matched_clip
        clip_paths.append(output_clip)

    bg_path = settings.videos_dir / f"{task_id}_bg.mp4"
    voice_path = settings.voice_dir / f"{task_id}.m4a"
    with_voice_path = settings.videos_dir / f"{task_id}_with_voice.mp4"
    final_path = settings.videos_dir / f"{task_id}.mp4"

    _concat_video(clip_paths, bg_path)
    _concat_audio(segments, voice_path)
    run_ffmpeg(
        [
            ffmpeg_exe(),
            "-y",
            "-i",
            str(bg_path),
            "-i",
            str(voice_path),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(with_voice_path),
        ]
    )
    run_ffmpeg(
        [
            ffmpeg_exe(),
            "-y",
            "-i",
            str(with_voice_path),
            "-vf",
            _subtitle_filter_path(subtitle_path),
            "-c:a",
            "copy",
            str(final_path),
        ],
    )

    return {
        "output_path": str(final_path),
        "subtitle_path": str(subtitle_path),
        "output_url": to_static_url(final_path, settings.base_dir),
        "subtitle_url": to_static_url(subtitle_path, settings.base_dir),
    }
