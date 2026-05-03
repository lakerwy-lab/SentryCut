"""FastAPI entry point for the AI video mixer MVP backend."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import materials, scripts, tasks, videos
from app.config import ensure_directories, settings
from app.db.database import init_db


def create_app() -> FastAPI:
    ensure_directories()
    init_db()

    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials="*" not in settings.cors_allow_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/static/output", StaticFiles(directory=settings.output_dir), name="output")
    app.include_router(materials.router, prefix=settings.api_prefix)
    app.include_router(scripts.router, prefix=settings.api_prefix)
    app.include_router(videos.router, prefix=settings.api_prefix)
    app.include_router(tasks.router, prefix=settings.api_prefix)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
