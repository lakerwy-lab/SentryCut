# AI 视频素材混剪助手方案

## 1. 项目定位

本项目是一个面向个人开发者的 AI 视频素材混剪工具。

核心目标：

> 用户上传或导入一批视频素材，输入一段口播文案，系统自动从素材库中检索匹配画面，生成口播音频、字幕，并合成一个完整短视频。

第一版不追求复杂剪辑器，而是先跑通完整链路：

```text
上传素材视频
  ↓
建立素材索引
  ↓
输入口播文案
  ↓
AI 拆分分镜
  ↓
根据分镜从素材库匹配视频片段
  ↓
生成口播音频
  ↓
生成字幕
  ↓
FFmpeg 合成视频
  ↓
前端预览和下载
```

---

## 2. 技术选型

### 2.1 前端

```text
Vue3
Vite
TypeScript
Element Plus
Axios
Vue Router
Pinia
```

前端主要负责：

- 素材上传
- 素材列表展示
- 文案输入
- 配音音色选择
- 视频比例选择
- 分镜预览
- 任务进度展示
- 视频预览和下载

### 2.2 后端

```text
Python
FastAPI
SQLite
SentrySearch
FFmpeg
edge-tts
```

后端主要负责：

- 接收素材上传
- 保存素材文件
- 调用 SentrySearch 建立素材索引
- 调用 LLM 拆分文案为分镜
- 根据 visual_query 检索匹配素材片段
- 生成 TTS 口播音频
- 生成字幕文件
- 调用 FFmpeg 合成最终视频
- 提供任务状态查询接口

### 2.3 核心能力对应关系

| 能力 | 推荐技术 |
|---|---|
| 前端界面 | Vue3 + Element Plus |
| 后端 API | FastAPI |
| 素材检索 | SentrySearch |
| 向量库 | ChromaDB，沿用 SentrySearch |
| 视频处理 | FFmpeg |
| 配音生成 | edge-tts |
| 文案拆分 | LLM API，例如 OpenAI、DeepSeek、Qwen、Kimi |
| 数据库 | SQLite |
| 任务进度 | 第一版轮询，后续可升级 SSE |
| 文件存储 | 本地文件夹 |

---

## 3. MVP 功能范围

### 3.1 第一版必须做

```text
1. 支持上传视频素材
2. 支持素材列表展示
3. 支持触发素材索引
4. 支持输入口播文案
5. 支持选择视频比例：9:16 / 16:9 / 1:1
6. 支持选择配音音色
7. 支持 AI 生成分镜脚本
8. 支持每个分镜匹配素材片段
9. 支持生成口播音频
10. 支持生成字幕
11. 支持合成最终 MP4
12. 支持前端预览和下载
```

### 3.2 第一版暂不做

```text
1. 不做用户登录
2. 不做多租户
3. 不做权限系统
4. 不做复杂时间线编辑器
5. 不做多人协作
6. 不做在线发布
7. 不做声音克隆
8. 不做高级转场动画
9. 不做素材版权管理
10. 不做复杂后台管理系统
```

### 3.3 关键工程修订

本方案不收缩 MVP 范围，第一版仍然完整包含素材上传、素材库、索引、分镜、匹配、TTS、字幕、合成、预览下载。为了让实现更稳定，需要提前明确以下工程边界：

```text
1. /api/videos/render 是一键生成接口，负责统一编排 plan、match、tts、subtitle、render。
2. 索引任务和渲染任务统一使用 tasks 表和 /api/tasks/{task_id} 查询状态。
3. SentrySearch 后端通过 Python import 集成，不通过 CLI 调用。
4. 默认 embedding 后端使用已测通的 Gemini，ChromaDB 路径固定为 ai-video-mixer-api/data/chroma/，避免 CLI 默认目录和后端目录不一致。
5. LLM 返回的 estimated_duration 只作为估算值，最终时间线以每段 TTS 实际音频时长为准。
6. FFmpeg 不直接用 -c copy 拼接不同来源素材，所有片段先统一转码再拼接。
7. LLM 输出必须经过 JSON 解析和 Pydantic 校验，失败时重试 1 次，仍失败则任务 failed。
```

---

## 4. 系统架构

```text
ai-video-mixer
├─ frontend：Vue3 前端
│  ├─ 素材库页面
│  ├─ 创建视频页面
│  ├─ 任务详情页面
│  └─ 视频预览页面
│
├─ backend：FastAPI 后端
│  ├─ 素材管理 API
│  ├─ 分镜生成 API
│  ├─ 素材匹配 API
│  ├─ 视频生成 API
│  └─ 任务状态 API
│
├─ SentrySearch
│  ├─ 视频切片
│  ├─ embedding 生成
│  ├─ ChromaDB 向量检索
│  └─ 匹配片段裁剪
│
├─ FFmpeg
│  ├─ 视频裁剪
│  ├─ 视频缩放
│  ├─ 视频拼接
│  ├─ 字幕烧录
│  └─ 音视频合成
│
└─ 本地存储
   ├─ 原始素材
   ├─ 裁剪片段
   ├─ 口播音频
   ├─ 字幕文件
   └─ 最终视频
```

---

## 5. 项目目录设计

### 5.1 前端目录

```text
ai-video-mixer-web/
├─ src/
│  ├─ api/
│  │  ├─ material.ts
│  │  ├─ video.ts
│  │  └─ task.ts
│  │
│  ├─ views/
│  │  ├─ MaterialLibrary.vue
│  │  ├─ CreateVideo.vue
│  │  ├─ TaskDetail.vue
│  │  └─ VideoPreview.vue
│  │
│  ├─ components/
│  │  ├─ UploadPanel.vue
│  │  ├─ ScriptEditor.vue
│  │  ├─ SegmentTimeline.vue
│  │  ├─ ClipCard.vue
│  │  └─ RenderProgress.vue
│  │
│  ├─ router/
│  │  └─ index.ts
│  │
│  ├─ stores/
│  │  └─ task.ts
│  │
│  ├─ App.vue
│  └─ main.ts
│
├─ package.json
└─ vite.config.ts
```

### 5.2 后端目录

```text
ai-video-mixer-api/
├─ app/
│  ├─ main.py
│  │
│  ├─ api/
│  │  ├─ materials.py
│  │  ├─ scripts.py
│  │  ├─ videos.py
│  │  └─ tasks.py
│  │
│  ├─ services/
│  │  ├─ sentry_search_service.py
│  │  ├─ planner_service.py
│  │  ├─ tts_service.py
│  │  ├─ subtitle_service.py
│  │  └─ render_service.py
│  │
│  ├─ models/
│  │  ├─ material.py
│  │  ├─ task.py
│  │  └─ segment.py
│  │
│  ├─ db/
│  │  ├─ database.py
│  │  └─ schema.sql
│  │
│  └─ config.py
│
├─ materials/
│  └─ 原始素材视频
│
├─ clips/
│  └─ 匹配后裁剪片段
│
├─ output/
│  ├─ voice/
│  ├─ subtitles/
│  └─ videos/
│
├─ data/
│  ├─ app.db
│  └─ chroma/
│
├─ requirements.txt
└─ README.md
```

---

## 6. 前端页面设计

### 6.1 素材库页面

页面路径：

```text
/materials
```

功能：

```text
1. 上传视频素材
2. 查看素材列表
3. 查看素材状态
4. 触发素材建索引
5. 查看素材是否已索引
```

页面布局：

```text
-------------------------------------------------
| 素材库                                        |
-------------------------------------------------
| [上传视频] [建立索引]                         |
-------------------------------------------------
| 文件名        时长      状态        操作        |
| office.mp4    00:30    已上传      删除        |
| ai.mp4        01:12    已索引      删除        |
-------------------------------------------------
```

### 6.2 创建视频页面

页面路径：

```text
/create
```

功能：

```text
1. 输入口播文案
2. 选择视频比例
3. 选择配音音色
4. 生成分镜
5. 匹配素材
6. 一键生成视频
7. 展示任务进度
```

页面布局：

```text
-------------------------------------------------
| 创建 AI 混剪视频                              |
-------------------------------------------------
| 左侧：口播文案输入                            |
|                                               |
| [ 多行文本框 ]                                |
|                                               |
| 视频比例：[9:16] [16:9] [1:1]                 |
| 配音音色：[中文女声] [中文男声]               |
|                                               |
| [生成分镜] [匹配素材] [生成视频]              |
-------------------------------------------------
| 右侧：分镜预览                                |
| 1. 口播：现在很多企业都在做 AI Agent          |
|    画面：科技感办公室，AI大屏，团队讨论       |
|    素材：clip_001.mp4                         |
-------------------------------------------------
| 底部：生成进度                                |
| 正在合成视频 70%                              |
-------------------------------------------------
```

### 6.3 任务详情页面

页面路径：

```text
/tasks/:taskId
```

功能：

```text
1. 查看任务状态
2. 查看当前进度
3. 查看分镜列表
4. 查看每个分镜匹配到的视频片段
5. 查看错误信息
6. 完成后跳转预览
```

### 6.4 视频预览页面

页面路径：

```text
/preview/:taskId
```

功能：

```text
1. 播放生成的视频
2. 下载 MP4
3. 下载字幕 SRT
4. 查看使用到的素材片段
5. 重新生成
```

---

## 7. 后端接口设计

### 7.1 上传素材

```http
POST /api/materials/upload
```

请求：

```text
multipart/form-data
file: 视频文件
```

返回：

```json
{
  "material_id": "mat_001",
  "original_filename": "office.mp4",
  "stored_filename": "mat_001.mp4",
  "path": "materials/mat_001.mp4",
  "duration": 30.2,
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "status": "uploaded"
}
```

上传策略：

```text
1. 第一版支持 mp4 / mov。
2. 后端保存文件名使用 material_id + 原扩展名，原始文件名单独入库。
3. 上传后用 ffprobe 读取 duration / width / height / fps。
4. 同名文件不会覆盖。
5. 不支持的格式直接返回明确错误。
```

---

### 7.2 获取素材列表

```http
GET /api/materials
```

返回：

```json
{
  "items": [
    {
      "id": "mat_001",
      "original_filename": "office.mp4",
      "stored_filename": "mat_001.mp4",
      "path": "materials/mat_001.mp4",
      "duration": 30.2,
      "width": 1920,
      "height": 1080,
      "fps": 30,
      "status": "uploaded",
      "created_at": "2026-05-02 12:00:00"
    }
  ]
}
```

---

### 7.3 建立素材索引

```http
POST /api/materials/index
```

请求：

```json
{
  "material_ids": ["mat_001", "mat_002"]
}
```

返回：

```json
{
  "task_id": "index_001",
  "type": "index",
  "status": "pending"
}
```

处理逻辑：

```text
1. 读取素材文件
2. 创建 type=index 的任务记录
3. 通过 Python import 调用 SentrySearch 建索引
4. 切片
5. 生成 embedding
6. 写入 ai-video-mixer-api/data/chroma/
7. 记录 embedding_backend 和 embedding_model
8. 更新素材状态为 indexed
9. 更新任务状态为 completed
```

---

### 7.4 生成分镜脚本

```http
POST /api/scripts/plan
```

请求：

```json
{
  "script": "现在很多企业都在做 AI Agent...",
  "aspect_ratio": "9:16",
  "voice": "zh-CN-XiaoxiaoNeural"
}
```

返回：

```json
{
  "segments": [
    {
      "index": 1,
      "narration": "现在很多企业都在做 AI Agent",
      "visual_query": "科技感办公室，AI大屏，团队讨论",
      "estimated_duration": 3.5
    }
  ]
}
```

---

### 7.5 根据分镜匹配素材

```http
POST /api/videos/match-clips
```

请求：

```json
{
  "segments": [
    {
      "index": 1,
      "narration": "现在很多企业都在做 AI Agent",
      "visual_query": "科技感办公室，AI大屏，团队讨论",
      "estimated_duration": 3.5
    }
  ]
}
```

返回：

```json
{
  "segments": [
    {
      "index": 1,
      "narration": "现在很多企业都在做 AI Agent",
      "visual_query": "科技感办公室，AI大屏，团队讨论",
      "estimated_duration": 3.5,
      "source_file": "materials/mat_001.mp4",
      "source_start_time": 12.0,
      "source_end_time": 42.0,
      "similarity_score": 0.72,
      "matched_clip": "clips/clip_001.mp4"
    }
  ]
}
```

---

### 7.6 创建视频生成任务

```http
POST /api/videos/render
```

接口职责：

```text
1. /api/videos/render 是一键生成接口。
2. 当 segments 为空或不传时，后端自动执行：plan → match → tts → subtitle → render。
3. 当 segments 不为空时，后端使用前端传入的分镜和素材匹配结果直接渲染。
4. 这样既支持一键生成，也支持用户调整分镜或替换片段后重新生成。
```

请求：

```json
{
  "script": "现在很多企业都在做 AI Agent...",
  "voice": "zh-CN-XiaoxiaoNeural",
  "aspect_ratio": "9:16",
  "segments": [
    {
      "index": 1,
      "narration": "现在很多企业都在做 AI Agent",
      "visual_query": "科技感办公室，AI大屏，团队讨论",
      "estimated_duration": 3.5,
      "source_file": "materials/mat_001.mp4",
      "source_start_time": 12.0,
      "source_end_time": 42.0,
      "similarity_score": 0.72,
      "matched_clip": "clips/clip_001.mp4"
    }
  ]
}
```

如果用户直接一键生成，也可以传空分镜：

```json
{
  "script": "现在很多企业都在做 AI Agent...",
  "voice": "zh-CN-XiaoxiaoNeural",
  "aspect_ratio": "9:16",
  "segments": []
}
```

返回：

```json
{
  "task_id": "render_001",
  "type": "render",
  "status": "pending"
}
```

---

### 7.7 查询任务状态

```http
GET /api/tasks/{task_id}
```

返回：

```json
{
  "task_id": "render_001",
  "type": "render",
  "status": "rendering",
  "progress": 70,
  "current_step": "正在合成视频",
  "output_url": null,
  "error_message": null
}
```

完成后：

```json
{
  "task_id": "render_001",
  "type": "render",
  "status": "completed",
  "progress": 100,
  "current_step": "生成完成",
  "output_url": "/static/output/videos/final_001.mp4",
  "subtitle_url": "/static/output/subtitles/final_001.srt"
}
```

统一任务状态：

```text
pending
planning
matching
tts_generating
subtitle_generating
rendering
completed
failed
```

索引任务和视频生成任务都通过这个接口查询状态。前端根据 `type` 区分 index / render，根据 `status` 判断是否继续轮询。

---

## 8. 数据库设计

第一版使用 SQLite。

### 8.1 materials 表

```sql
CREATE TABLE materials (
  id TEXT PRIMARY KEY,
  original_filename TEXT NOT NULL,
  stored_filename TEXT NOT NULL,
  path TEXT NOT NULL,
  duration REAL,
  width INTEGER,
  height INTEGER,
  fps REAL,
  status TEXT DEFAULT 'uploaded',
  embedding_backend TEXT,
  embedding_model TEXT,
  index_error TEXT,
  created_at TEXT NOT NULL
);
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 素材 ID |
| original_filename | 用户上传时的原始文件名 |
| stored_filename | 后端保存的唯一文件名 |
| path | 本地路径 |
| duration | 视频时长 |
| width | 视频宽度 |
| height | 视频高度 |
| fps | 视频帧率 |
| status | uploaded / indexing / indexed / failed |
| embedding_backend | 索引使用的后端，默认 gemini |
| embedding_model | 索引使用的模型，默认 gemini-embedding-2-preview |
| index_error | 索引失败时的错误信息 |
| created_at | 创建时间 |

---

### 8.2 tasks 表

索引任务和视频生成任务统一使用 `tasks` 表。`type` 用于区分任务类型，`status` 用于前端判断是否继续轮询。

```sql
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,
  status TEXT DEFAULT 'pending',
  type TEXT NOT NULL,
  progress INTEGER DEFAULT 0,
  current_step TEXT,
  error_message TEXT,
  result_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  completed_at TEXT
);
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 任务 ID |
| type | index / render |
| status | pending / planning / matching / tts_generating / subtitle_generating / rendering / completed / failed |
| progress | 进度百分比 |
| current_step | 当前步骤 |
| error_message | 错误信息 |
| result_json | 任务结果 JSON，例如 output_url、subtitle_url、indexed_count |
| created_at | 创建时间 |
| updated_at | 更新时间 |
| completed_at | 完成时间 |

---

### 8.3 render_segments 表

```sql
CREATE TABLE render_segments (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  segment_index INTEGER NOT NULL,
  narration TEXT NOT NULL,
  visual_query TEXT NOT NULL,
  estimated_duration REAL,
  actual_duration REAL,
  source_file TEXT,
  source_start_time REAL,
  source_end_time REAL,
  similarity_score REAL,
  matched_clip TEXT,
  clip_path TEXT,
  voice_path TEXT,
  subtitle_start REAL,
  subtitle_end REAL,
  created_at TEXT NOT NULL
);
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 分镜 ID |
| task_id | 所属任务 |
| segment_index | 分镜顺序 |
| narration | 口播文本 |
| visual_query | 检索画面的描述 |
| estimated_duration | LLM 估算时长 |
| actual_duration | TTS 音频实际时长 |
| source_file | 匹配到的原始素材路径 |
| source_start_time | 素材片段开始时间 |
| source_end_time | 素材片段结束时间 |
| similarity_score | SentrySearch 相似度分数 |
| matched_clip | 匹配后裁剪片段路径 |
| clip_path | 统一转码后的片段路径 |
| voice_path | 当前分镜的 TTS 音频路径 |
| subtitle_start | 当前分镜字幕开始时间 |
| subtitle_end | 当前分镜字幕结束时间 |
| created_at | 创建时间 |

---

## 9. 核心任务流

### 9.1 一键生成视频流程

```text
1. 创建 type=render 的任务记录，状态 pending
2. 如果请求未传 segments，更新状态 planning，调用 LLM 生成分镜 segments
3. 对 LLM 输出做 JSON 解析和 Pydantic 校验，失败时重试 1 次
4. 更新状态 matching，调用 SentrySearch 匹配每个分镜的视频片段
5. 保存 source_file、source_start_time、source_end_time、similarity_score
6. 更新状态 tts_generating，为每个 segment 单独生成一段 TTS 音频
7. 读取每段 TTS 音频真实时长 actual_duration
8. 更新状态 subtitle_generating，根据累计 actual_duration 生成 subtitle_start / subtitle_end 和 subtitle.srt
9. 更新状态 rendering，按每段 actual_duration 裁剪素材并统一转码
10. 拼接统一转码后的片段，混入口播音频，烧录字幕
11. 更新状态 completed，写入 output_url、subtitle_url
12. 任意步骤失败时更新状态 failed，保存 error_message
```

### 9.2 后端伪代码

```python
def run_render_pipeline(task_id, req):
    try:
        if req.segments:
            segments = req.segments
        else:
            update_task(task_id, "planning", 10, "正在生成分镜")
            segments = plan_script_with_validation(req.script)

        update_task(task_id, "matching", 30, "正在匹配素材")
        segments = match_clips_with_sentrysearch(segments)

        update_task(task_id, "tts_generating", 50, "正在生成口播")
        segments = generate_segment_tts(segments, req.voice)
        # generate_segment_tts 写入 voice_path 和 actual_duration

        update_task(task_id, "subtitle_generating", 65, "正在生成字幕")
        subtitle_path = generate_subtitle_by_actual_duration(segments)
        # subtitle_start / subtitle_end 由累计 actual_duration 计算

        update_task(task_id, "rendering", 80, "正在合成视频")
        output_path = render_final_video(
            segments=segments,
            subtitle_path=subtitle_path,
            aspect_ratio=req.aspect_ratio,
        )

        update_task(
            task_id,
            "completed",
            100,
            "生成完成",
            result_json={
                "output_url": to_static_url(output_path),
                "subtitle_url": to_static_url(subtitle_path),
            },
        )
    except Exception as exc:
        update_task(task_id, "failed", 100, "生成失败", error_message=str(exc))
```

---

## 10. LLM 分镜 Prompt

```text
你是一个短视频分镜导演。

请把用户输入的口播文案拆成适合短视频混剪的分镜脚本。

要求：
1. 每个分镜包含 narration、visual_query、estimated_duration。
2. narration 是这一段要朗读的口播文本。
3. visual_query 是用于从视频素材库检索画面的描述，要具体、可视化。
4. estimated_duration 根据 narration 字数估算，中文每秒约 4～5 个字。
5. visual_query 要适合检索视频画面，不要太抽象。
6. 输出 JSON 数组，不要输出解释。

用户文案：
{{script}}

输出格式：
[
  {
    "narration": "现在很多企业都在做 AI Agent",
    "visual_query": "科技感办公室，AI大屏，团队讨论，企业数字化",
    "estimated_duration": 3.5
  }
]
```

LLM 输出处理要求：

```text
1. 后端先解析 JSON，不接受 Markdown 代码块之外的解释性文本。
2. 使用 Pydantic 校验 segments 数组。
3. narration、visual_query 不能为空。
4. estimated_duration 必须大于 0。
5. JSON 解析失败或字段缺失时，使用同一 prompt 追加“只输出合法 JSON”重试 1 次。
6. 仍失败则任务状态改为 failed，并保存原始错误信息。
```

---

## 11. FFmpeg 合成方案

### 11.1 合成原则

不同素材的编码、分辨率、帧率和音轨可能不一致，第一版不直接用 `-c copy` 拼接原始片段。所有 matched clip 必须先统一转码，再拼接。

统一规则：

```text
1. 9:16 输出尺寸：1080x1920
2. 16:9 输出尺寸：1920x1080
3. 1:1 输出尺寸：1080x1080
4. 输出 fps：30
5. 像素格式：yuv420p
6. 视频编码：优先 libx264，不可用时 fallback 到 mpeg4
7. 去掉原素材音频：-an
8. 最终视频只混入 edge-tts 生成的口播音频
```

### 11.2 统一竖屏 9:16

```bash
ffmpeg -i input.mp4 \
-ss 12.0 -t 3.8 \
-vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p" \
-an -c:v libx264 -preset veryfast -crf 20 output_vertical.mp4
```

### 11.3 统一横屏 16:9

```bash
ffmpeg -i input.mp4 \
-ss 12.0 -t 3.8 \
-vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p" \
-an -c:v libx264 -preset veryfast -crf 20 output_horizontal.mp4
```

### 11.4 统一方屏 1:1

```bash
ffmpeg -i input.mp4 \
-ss 12.0 -t 3.8 \
-vf "scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080,fps=30,format=yuv420p" \
-an -c:v libx264 -preset veryfast -crf 20 output_square.mp4
```

如果当前 FFmpeg 不支持 `libx264`，使用 `mpeg4` fallback：

```bash
ffmpeg -i input.mp4 \
-ss 12.0 -t 3.8 \
-vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p" \
-an -c:v mpeg4 -q:v 5 output_vertical.mp4
```

### 11.5 拼接统一转码后的片段

生成 `concat.txt`：

```text
file 'clip_001_vertical.mp4'
file 'clip_002_vertical.mp4'
file 'clip_003_vertical.mp4'
```

执行：

```bash
ffmpeg -f concat -safe 0 -i concat.txt \
-c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p output/bg.mp4
```

### 11.6 混入口播音频

每个 segment 单独生成 TTS 音频后，先按顺序拼接口播音频，再与背景视频合成。

生成 `voice_concat.txt`：

```text
file 'voice_001.mp3'
file 'voice_002.mp3'
file 'voice_003.mp3'
```

拼接口播：

```bash
ffmpeg -f concat -safe 0 -i voice_concat.txt -c:a libmp3lame output/voice.mp3
```

```bash
ffmpeg -i output/bg.mp4 -i output/voice.mp3 \
-c:v copy -c:a aac -shortest output/with_voice.mp4
```

### 11.7 烧录字幕

```bash
ffmpeg -i output/with_voice.mp4 \
-vf "subtitles=output/subtitle.srt" \
-c:v libx264 -preset veryfast -crf 20 -c:a copy output/final.mp4
```

字幕时间线根据每个 segment 的 `actual_duration` 计算：

```text
segment_001 subtitle_start = 0
segment_001 subtitle_end = segment_001.actual_duration
segment_002 subtitle_start = segment_001.subtitle_end
segment_002 subtitle_end = segment_002.subtitle_start + segment_002.actual_duration
```

---

## 12. 前端 API 封装示例

`src/api/video.ts`

```ts
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
});

export function planScript(data: {
  script: string;
  aspect_ratio: string;
  voice: string;
}) {
  return api.post("/scripts/plan", data);
}

export function matchClips(data: {
  segments: Segment[];
}) {
  return api.post("/videos/match-clips", data);
}

export function renderVideo(data: {
  script: string;
  voice: string;
  aspect_ratio: string;
  segments?: Segment[];
}) {
  return api.post("/videos/render", data);
}

export function getTask(taskId: string) {
  return api.get(`/tasks/${taskId}`);
}

export interface Segment {
  index: number;
  narration: string;
  visual_query: string;
  estimated_duration?: number;
  actual_duration?: number;
  source_file?: string;
  source_start_time?: number;
  source_end_time?: number;
  similarity_score?: number;
  matched_clip?: string;
  clip_path?: string;
  voice_path?: string;
  subtitle_start?: number;
  subtitle_end?: number;
}
```

---

## 13. 前端核心页面示例

`CreateVideo.vue`

```vue
<template>
  <div class="page">
    <el-card>
      <template #header>创建 AI 混剪视频</template>

      <el-form label-width="100px">
        <el-form-item label="口播文案">
          <el-input
            v-model="script"
            type="textarea"
            :rows="8"
            placeholder="请输入口播文案"
          />
        </el-form-item>

        <el-form-item label="视频比例">
          <el-radio-group v-model="aspectRatio">
            <el-radio-button label="9:16" />
            <el-radio-button label="16:9" />
            <el-radio-button label="1:1" />
          </el-radio-group>
        </el-form-item>

        <el-form-item label="配音音色">
          <el-select v-model="voice">
            <el-option label="中文女声-晓晓" value="zh-CN-XiaoxiaoNeural" />
            <el-option label="中文男声-云希" value="zh-CN-YunxiNeural" />
            <el-option label="中文男声-云健" value="zh-CN-YunjianNeural" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleGenerate">
            一键生成视频
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top: 16px">
      <template #header>生成进度</template>
      <el-progress :percentage="progress" />
      <p>{{ currentStep }}</p>
    </el-card>

    <el-card v-if="outputUrl" style="margin-top: 16px">
      <template #header>视频预览</template>
      <video :src="outputUrl" controls style="width: 320px" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { renderVideo, getTask } from "@/api/video";

const script = ref("");
const aspectRatio = ref("9:16");
const voice = ref("zh-CN-XiaoxiaoNeural");
const progress = ref(0);
const currentStep = ref("等待生成");
const outputUrl = ref("");

async function handleGenerate() {
  const res = await renderVideo({
    script: script.value,
    segments: [],
    voice: voice.value,
    aspect_ratio: aspectRatio.value,
  });

  const taskId = res.data.task_id;
  pollTask(taskId);
}

function pollTask(taskId: string) {
  const timer = setInterval(async () => {
    const res = await getTask(taskId);
    const task = res.data;

    progress.value = task.progress;
    currentStep.value = task.current_step;

    if (task.status === "completed") {
      outputUrl.value = `http://localhost:8000${task.output_url}`;
      clearInterval(timer);
    }

    if (task.status === "failed") {
      clearInterval(timer);
    }
  }, 1500);
}
</script>

<style scoped>
.page {
  padding: 24px;
}
</style>
```

---

## 14. 开发计划

第一版不收缩 MVP 功能，但开发顺序调整为先建立稳定素材和任务基础，再跑通一键生成，最后补齐前端和手动调整能力。

### 阶段 1：后端素材上传、索引、素材列表、任务查询

目标：

```text
先让素材库和索引任务稳定可用，为后续 render 提供可检索素材。
```

任务：

```text
1. 初始化 FastAPI 项目
2. 配置静态文件目录和本地存储目录
3. 实现 materials 表、tasks 表
4. 实现 /api/materials/upload
5. 实现 /api/materials
6. 实现 /api/materials/index
7. 实现 /api/tasks/{task_id}
8. 通过 Python import 集成 SentrySearch
9. 固定 ChromaDB 路径为 ai-video-mixer-api/data/chroma/
10. 保存 embedding_backend 和 embedding_model
```

验收标准：

```text
前端或接口工具可以上传 mp4 / mov，后端保存唯一文件名，读取视频元信息，触发索引任务，并通过 /api/tasks/{task_id} 看到索引完成。
```

---

### 阶段 2：后端一键 render 完整链路

目标：

```text
用 /api/videos/render 跑通 plan → match → tts → subtitle → render 完整链路。
```

任务：

```text
1. 实现 /api/videos/render
2. 实现 /api/scripts/plan
3. 实现 LLM JSON 输出解析、Pydantic 校验和失败重试
4. 实现 /api/videos/match-clips
5. 接入 SentrySearch 检索素材
6. 实现每个 segment 单独生成 edge-tts 音频
7. 读取每段 TTS 实际时长 actual_duration
8. 按 actual_duration 生成字幕时间线和 SRT
9. 按 actual_duration 裁剪、统一转码、拼接视频片段
10. 混入口播音频并烧录字幕
11. 将 output_url、subtitle_url 写入 tasks.result_json
```

验收标准：

```text
输入一段文案，接口返回 task_id；任务完成后 output/videos 生成 final.mp4，output/subtitles 生成 final.srt，音频、字幕和画面时间基本同步。
```

---

### 阶段 3：前端素材库、创建页面、任务轮询、视频预览

目标：

```text
前端可以完成素材上传、索引、输入文案、一键生成视频、查看进度和预览下载。
```

任务：

```text
1. 初始化 Vue3 + Vite + TypeScript 项目
2. 安装 Element Plus、Axios、Vue Router、Pinia
3. 实现 MaterialLibrary.vue
4. 实现 CreateVideo.vue
5. 实现 TaskDetail.vue
6. 实现 VideoPreview.vue
7. 封装 material.ts、video.ts、task.ts
8. 实现任务进度轮询
9. 实现视频预览和下载
```

验收标准：

```text
用户可以在前端上传素材并建立索引，输入口播文案后点击“一键生成视频”，能看到进度，完成后能播放和下载 MP4 / SRT。
```

---

### 阶段 4：分镜预览、重新匹配、手动替换片段

目标：

```text
用户可以在生成最终视频前查看 AI 分镜和素材匹配结果，并进行基础人工干预。
```

任务：

```text
1. 前端展示分镜列表
2. 展示 narration、visual_query、estimated_duration
3. 展示 source_file、source_start_time、source_end_time、similarity_score
4. 支持重新匹配单个分镜
5. 支持每个分镜返回 top3 候选
6. 支持用户替换 matched_clip
7. 支持带 segments 调用 /api/videos/render 重新生成
```

验收标准：

```text
用户生成视频前，可以看到每句口播对应的视频画面，可以重新匹配或替换素材片段，再生成最终视频。
```

---

### 阶段 5：字幕样式、BGM、top3 候选、效果优化

目标：

```text
让生成视频更像可发布短视频。
```

任务：

```text
1. 优化字幕字体、字号、描边、位置
2. 增加背景音乐
3. 增加片段去重
4. 支持 9:16 / 16:9 / 1:1 的稳定合成预设
5. 优化 top3 素材候选展示
6. 优化片段裁剪和画面节奏
```

验收标准：

```text
生成的视频画面不重复，字幕清晰，口播和画面节奏基本匹配，整体达到可预览和二次调整的短视频效果。
```

---

## 15. 启动命令

### 15.1 前端启动

```bash
cd ai-video-mixer-web
npm install
npm run dev
```

### 15.2 后端启动

```bash
cd ai-video-mixer-api
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 15.3 依赖检查

```bash
ffmpeg -version
python --version
node -v
npm -v
```

---

## 16. 后续升级方向

| 升级项 | 说明 |
|---|---|
| SSE 实时进度 | 替代前端轮询 |
| Celery + Redis | 支持多个任务并发 |
| Qdrant | 替换 ChromaDB，增强向量检索能力 |
| Remotion | 做高级字幕、转场、模板化视频 |
| MinIO | 替换本地文件夹，统一管理素材 |
| PostgreSQL | 替换 SQLite，支持更复杂查询 |
| 素材手动打标签 | 提高匹配质量 |
| 多候选片段 | 每个分镜返回 top3 让用户选择 |
| 时间线编辑器 | 支持用户拖拽调整片段 |
| 封面生成 | 自动生成标题、封面和标签 |
| 背景音乐 | 自动匹配 BGM |
| 发布接口 | 对接抖音、视频号、小红书等平台 |

---

## 17. MVP 总结

第一版项目不要做复杂，最重要的是跑通：

```text
素材库 → 文案 → 分镜 → 检索素材 → 配音 → 字幕 → 合成 → 预览下载
```

推荐最终 MVP 定义：

```text
项目名：AI 视频素材混剪助手

前端：
Vue3 + Element Plus
提供素材上传、文案输入、分镜预览、任务进度、视频预览下载。

后端：
Python + FastAPI
负责素材保存、调用 SentrySearch、LLM 分镜、TTS 配音、字幕生成、FFmpeg 合成。

第一版目标：
用户上传素材后，输入一段口播文案，系统自动从素材库匹配视频片段，并生成带口播和字幕的短视频。
```

一句话落地路线：

```text
SentrySearch 负责“从素材库找画面”
LLM 负责“把文案拆成分镜”
edge-tts 负责“生成口播”
FFmpeg 负责“拼接、裁剪、字幕、合成”
Vue3 负责“前端操作界面”
FastAPI 负责“后端任务编排”
```
