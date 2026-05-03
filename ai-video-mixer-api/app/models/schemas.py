"""Pydantic request and response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


AspectRatio = Literal["9:16", "16:9", "1:1"]
TaskType = Literal["index", "render"]


class MaterialOut(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    path: str
    duration: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    status: str
    embedding_backend: str | None = None
    embedding_model: str | None = None
    index_error: str | None = None
    created_at: str


class MaterialListOut(BaseModel):
    items: list[MaterialOut]


class IndexRequest(BaseModel):
    material_ids: list[str] = Field(default_factory=list)


class Segment(BaseModel):
    index: int = Field(ge=1)
    narration: str = Field(min_length=1)
    visual_query: str = Field(min_length=1)
    estimated_duration: float | None = Field(default=None, gt=0)
    actual_duration: float | None = Field(default=None, gt=0)
    source_file: str | None = None
    source_start_time: float | None = Field(default=None, ge=0)
    source_end_time: float | None = Field(default=None, ge=0)
    similarity_score: float | None = None
    matched_clip: str | None = None
    clip_path: str | None = None
    voice_path: str | None = None
    subtitle_start: float | None = Field(default=None, ge=0)
    subtitle_end: float | None = Field(default=None, ge=0)


class PlanRequest(BaseModel):
    script: str = Field(min_length=1)
    aspect_ratio: AspectRatio = "9:16"
    voice: str = "zh-CN-XiaoxiaoNeural"


class PlanResponse(BaseModel):
    segments: list[Segment]


class MatchRequest(BaseModel):
    segments: list[Segment]
    results: int = Field(default=1, ge=1, le=10)


class MatchResponse(BaseModel):
    segments: list[Segment]


class RenderRequest(BaseModel):
    script: str = Field(min_length=1)
    voice: str = "zh-CN-XiaoxiaoNeural"
    aspect_ratio: AspectRatio = "9:16"
    segments: list[Segment] = Field(default_factory=list)


class TaskOut(BaseModel):
    task_id: str
    type: TaskType
    status: str
    progress: int
    current_step: str | None = None
    output_url: str | None = None
    subtitle_url: str | None = None
    error_message: str | None = None
    result_json: dict | None = None
    created_at: str
    updated_at: str
    completed_at: str | None = None


class TaskCreated(BaseModel):
    task_id: str
    type: TaskType
    status: str
