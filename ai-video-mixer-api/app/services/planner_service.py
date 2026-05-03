"""LLM-backed script planning with validation and fallback."""

from __future__ import annotations

import json
import os
import re

from pydantic import TypeAdapter, ValidationError

from app.config import settings
from app.models.schemas import Segment


SEGMENT_ADAPTER = TypeAdapter(list[Segment])


def _prompt(script: str, *, retry: bool = False) -> str:
    suffix = "\n只输出合法 JSON 数组，不要 Markdown，不要解释。" if retry else ""
    return f"""你是一个短视频分镜导演。

请把用户输入的口播文案拆成适合短视频混剪的分镜脚本。

要求：
1. 每个分镜包含 index、narration、visual_query、estimated_duration。
2. narration 是这一段要朗读的口播文本。
3. visual_query 是用于从视频素材库检索画面的描述，要具体、可视化。
4. estimated_duration 根据 narration 字数估算，中文每秒约 4 到 5 个字。
5. visual_query 要适合检索视频画面，不要太抽象。
6. 必须覆盖用户原文的全部信息。
7. narration 只能来自用户原文的断句或轻微整理，不要新增观点、问题或例子。
8. 输出 JSON 数组，不要输出解释。

用户文案：
{script}

输出格式：
[
  {{
    "index": 1,
    "narration": "现在很多企业都在做 AI Agent",
    "visual_query": "科技感办公室，AI大屏，团队讨论，企业数字化",
    "estimated_duration": 3.5
  }}
]
{suffix}"""


def _extract_json_array(text: str) -> str:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.S | re.I)
    if fence:
        cleaned = fence.group(1).strip()
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("LLM response did not contain a JSON array.")
    return cleaned[start : end + 1]


def _validate_segments(text: str) -> list[Segment]:
    raw = json.loads(_extract_json_array(text))
    segments = SEGMENT_ADAPTER.validate_python(raw)
    for i, segment in enumerate(segments, 1):
        segment.index = i
    return segments


def _generate_with_gemini(script: str, *, retry: bool = False) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    from google import genai

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=settings.llm_model,
        contents=_prompt(script, retry=retry),
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty planning response.")
    return text


def _rule_based_segments(script: str) -> list[Segment]:
    parts = [p.strip() for p in re.split(r"[。！？!?；;\n]+", script) if p.strip()]
    if not parts:
        parts = [script.strip()]

    segments: list[Segment] = []
    buffer = ""
    for part in parts:
        if len(buffer) + len(part) <= 42:
            buffer = f"{buffer}{part}" if not buffer else f"{buffer}，{part}"
        else:
            if buffer:
                segments.append(_segment_from_text(len(segments) + 1, buffer))
            buffer = part
    if buffer:
        segments.append(_segment_from_text(len(segments) + 1, buffer))
    return segments


def _segment_from_text(index: int, text: str) -> Segment:
    estimated = max(2.0, round(len(text) / 4.5, 1))
    return Segment(
        index=index,
        narration=text,
        visual_query=text,
        estimated_duration=estimated,
    )


def plan_script(script: str) -> list[Segment]:
    last_error: Exception | None = None
    for retry in (False, True):
        try:
            return _validate_segments(_generate_with_gemini(script, retry=retry))
        except (json.JSONDecodeError, ValidationError, ValueError, RuntimeError) as exc:
            last_error = exc

    if settings.allow_rule_based_planner_fallback and not os.environ.get("GEMINI_API_KEY"):
        return _rule_based_segments(script)

    raise RuntimeError(f"Failed to generate valid segment JSON: {last_error}")
