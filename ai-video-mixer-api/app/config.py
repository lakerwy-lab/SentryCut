"""Application configuration and local paths."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = BASE_DIR.parent
SENTRYSEARCH_REPO = WORKSPACE_DIR / "sentrysearch"

if SENTRYSEARCH_REPO.exists():
    sys.path.insert(0, str(SENTRYSEARCH_REPO))

load_dotenv(BASE_DIR / ".env")
load_dotenv(SENTRYSEARCH_REPO / ".env.local")
load_dotenv(SENTRYSEARCH_REPO / ".env")


class Settings:
    app_name = "AI Video Mixer API"
    api_prefix = "/api"

    base_dir = BASE_DIR
    materials_dir = BASE_DIR / "materials"
    clips_dir = BASE_DIR / "clips"
    output_dir = BASE_DIR / "output"
    voice_dir = output_dir / "voice"
    subtitles_dir = output_dir / "subtitles"
    videos_dir = output_dir / "videos"
    data_dir = BASE_DIR / "data"
    chroma_dir = data_dir / "chroma"
    db_path = data_dir / "app.db"

    embedding_backend = os.getenv("EMBEDDING_BACKEND", "gemini")
    embedding_model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2-preview")
    llm_model = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
    default_voice = os.getenv("DEFAULT_TTS_VOICE", "zh-CN-XiaoxiaoNeural")

    chunk_duration = int(os.getenv("SENTRYSEARCH_CHUNK_DURATION", "30"))
    chunk_overlap = int(os.getenv("SENTRYSEARCH_CHUNK_OVERLAP", "5"))
    target_resolution = int(os.getenv("SENTRYSEARCH_TARGET_RESOLUTION", "480"))
    target_fps = int(os.getenv("SENTRYSEARCH_TARGET_FPS", "5"))
    search_results = int(os.getenv("SENTRYSEARCH_RESULTS", "3"))

    allow_rule_based_planner_fallback = os.getenv("ALLOW_PLANNER_FALLBACK", "1") == "1"
    allow_silent_tts_fallback = os.getenv("ALLOW_TTS_FALLBACK", "1") == "1"
    cors_allow_origins = [
        origin.strip()
        for origin in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
        if origin.strip()
    ]


settings = Settings()


def ensure_directories() -> None:
    for path in (
        settings.materials_dir,
        settings.clips_dir,
        settings.voice_dir,
        settings.subtitles_dir,
        settings.videos_dir,
        settings.data_dir,
        settings.chroma_dir,
    ):
        path.mkdir(parents=True, exist_ok=True)
