# AI 视频素材混剪助手 - 后端

FastAPI 后端，已完成方案中的阶段 1 和阶段 2：

- 阶段 1：素材上传、素材列表、素材索引、任务查询
- 阶段 2：一键 render 编排链路：`plan -> match -> tts -> subtitle -> render`

## 启动

```powershell
cd ai-video-mixer-api
uv venv
uv pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

接口文档：

```text
http://localhost:8000/docs
```

静态文件只暴露生成结果，不暴露数据库、ChromaDB、上传原素材或日志：

```text
http://localhost:8000/static/output/videos/<task_id>.mp4
http://localhost:8000/static/output/subtitles/<task_id>.srt
```

## 环境配置

默认读取：

```text
ai-video-mixer-api/.env
sentrysearch/.env.local
sentrysearch/.env
```

需要 Gemini key：

```env
GEMINI_API_KEY=your-key
```

可选配置：

```env
GEMINI_TEXT_MODEL=gemini-2.5-flash
EMBEDDING_BACKEND=gemini
DEFAULT_TTS_VOICE=zh-CN-XiaoxiaoNeural
ALLOW_PLANNER_FALLBACK=1
ALLOW_TTS_FALLBACK=1
CORS_ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## 已实现接口

### 上传素材

```http
POST /api/materials/upload
```

`multipart/form-data`：

```text
file: mp4 或 mov
```

### 获取素材列表

```http
GET /api/materials
```

### 建立素材索引

```http
POST /api/materials/index
```

```json
{
  "material_ids": ["mat_xxx"]
}
```

`material_ids` 为空时索引全部素材。返回 `task_id`，用 `/api/tasks/{task_id}` 轮询。

### 生成分镜

```http
POST /api/scripts/plan
```

```json
{
  "script": "现在很多企业都在做 AI Agent...",
  "aspect_ratio": "9:16",
  "voice": "zh-CN-XiaoxiaoNeural"
}
```

### 匹配素材片段

```http
POST /api/videos/match-clips
```

```json
{
  "segments": [
    {
      "index": 1,
      "narration": "现在很多企业都在做 AI Agent",
      "visual_query": "科技感办公室，AI 大屏，团队讨论",
      "estimated_duration": 3.5
    }
  ]
}
```

### 一键生成视频

```http
POST /api/videos/render
```

```json
{
  "script": "现在很多企业都在做 AI Agent...",
  "voice": "zh-CN-XiaoxiaoNeural",
  "aspect_ratio": "9:16",
  "segments": []
}
```

当 `segments` 为空时，后端自动执行：

```text
plan -> match -> tts -> subtitle -> render
```

当 `segments` 不为空时，使用传入分镜直接渲染，便于后续前端手动调整后重新生成。

### 查询任务

```http
GET /api/tasks/{task_id}
```

状态：

```text
pending / indexing / planning / matching / tts_generating / subtitle_generating / rendering / completed / failed
```

## 实现说明

- SQLite 数据库：`ai-video-mixer-api/data/app.db`
- ChromaDB 路径：`ai-video-mixer-api/data/chroma/`
- SentrySearch 通过 Python import 集成，不通过 CLI 调用；`requirements.txt` 使用 GitHub 依赖，若本地存在同级 `sentrysearch/` 目录，开发环境会优先使用本地源码
- LLM 分镜输出会 JSON 解析并用 Pydantic 校验，失败重试 1 次
- 每个 segment 单独生成 TTS，以实际音频时长生成字幕时间线
- FFmpeg 合成时每个片段先统一转码，再拼接，避免直接 `-c copy` 拼接不同素材
- 手动传入 `segments.source_file` 时，只允许已索引素材或 `materials/` 目录下的素材路径

## 下一步

- 阶段 3：实现 Vue3 前端素材库、创建视频页、任务详情页、视频预览页
- 阶段 4：分镜预览、重新匹配、手动替换片段
- 阶段 5：字幕样式、BGM、top3 候选和效果优化
