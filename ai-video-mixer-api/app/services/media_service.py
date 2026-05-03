"""Media probing and ffmpeg helpers."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from app.config import settings  # noqa: F401 - imports sentrysearch path setup
from sentrysearch.chunker import _get_ffmpeg_executable, _get_video_duration


def ffmpeg_exe() -> str:
    return _get_ffmpeg_executable()


def run_ffmpeg(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(args, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg command failed")
    return result


def probe_media(path: str | Path) -> dict:
    path = Path(path)
    duration = _get_video_duration(str(path))
    width = None
    height = None
    fps = None

    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        result = subprocess.run(
            [
                ffprobe,
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_streams",
                "-show_format",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        info = json.loads(result.stdout)
        video = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
        if video:
            width = video.get("width")
            height = video.get("height")
            rate = video.get("avg_frame_rate") or video.get("r_frame_rate")
            if rate and rate != "0/0":
                num, den = rate.split("/")
                fps = round(float(num) / float(den), 3) if float(den) else None
        return {"duration": duration, "width": width, "height": height, "fps": fps}

    result = subprocess.run(
        [ffmpeg_exe(), "-i", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    stderr = result.stderr
    size_match = re.search(r",\s*(\d{2,5})x(\d{2,5})[\s,]", stderr)
    fps_match = re.search(r"(\d+(?:\.\d+)?)\s+fps", stderr)
    if size_match:
        width = int(size_match.group(1))
        height = int(size_match.group(2))
    if fps_match:
        fps = float(fps_match.group(1))
    return {"duration": duration, "width": width, "height": height, "fps": fps}


def media_duration(path: str | Path) -> float:
    return float(_get_video_duration(str(path)))


def to_static_url(path: str | Path, base_dir: Path) -> str:
    rel = Path(path).resolve().relative_to(base_dir.resolve()).as_posix()
    return f"/static/{rel}"
