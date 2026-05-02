# AI 视频素材混剪助手 MVP 方案

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
  "filename": "office.mp4",
  "path": "materials/office.mp4",
  "status": "uploaded"
}
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
      "filename": "office.mp4",
      "path": "materials/office.mp4",
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
  "status": "running"
}
```

处理逻辑：

```text
1. 读取素材文件
2. 调用 SentrySearch 建索引
3. 切片
4. 生成 embedding
5. 写入 ChromaDB
6. 更新素材状态为 indexed
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
      "duration": 3.5
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
      "duration": 3.5
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
      "matched_clip": "clips/clip_001.mp4",
      "duration": 3.5
    }
  ]
}
```

---

### 7.6 创建视频生成任务

```http
POST /api/videos/render
```

请求：

```json
{
  "script": "现在很多企业都在做 AI Agent...",
  "segments": [
    {
      "index": 1,
      "narration": "现在很多企业都在做 AI Agent",
      "visual_query": "科技感办公室，AI大屏，团队讨论",
      "matched_clip": "clips/clip_001.mp4",
      "duration": 3.5
    }
  ],
  "voice": "zh-CN-XiaoxiaoNeural",
  "aspect_ratio": "9:16"
}
```

返回：

```json
{
  "task_id": "render_001",
  "status": "running"
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
  "status": "completed",
  "progress": 100,
  "current_step": "生成完成",
  "output_url": "/static/output/videos/final_001.mp4",
  "subtitle_url": "/static/output/subtitles/final_001.srt"
}
```

---

## 8. 数据库设计

第一版使用 SQLite。

### 8.1 materials 表

```sql
CREATE TABLE materials (
  id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  path TEXT NOT NULL,
  duration REAL,
  status TEXT DEFAULT 'uploaded',
  created_at TEXT NOT NULL
);
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 素材 ID |
| filename | 文件名 |
| path | 本地路径 |
| duration | 视频时长 |
| status | uploaded / indexing / indexed / failed |
| created_at | 创建时间 |

---

### 8.2 render_tasks 表

```sql
CREATE TABLE render_tasks (
  id TEXT PRIMARY KEY,
  script TEXT NOT NULL,
  voice TEXT,
  aspect_ratio TEXT,
  status TEXT DEFAULT 'pending',
  progress INTEGER DEFAULT 0,
  current_step TEXT,
  output_path TEXT,
  subtitle_path TEXT,
  error_message TEXT,
  created_at TEXT NOT NULL
);
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 任务 ID |
| script | 原始口播文案 |
| voice | 配音音色 |
| aspect_ratio | 视频比例 |
| status | pending / running / completed / failed |
| progress | 进度百分比 |
| current_step | 当前步骤 |
| output_path | 输出视频路径 |
| subtitle_path | 字幕路径 |
| error_message | 错误信息 |
| created_at | 创建时间 |

---

### 8.3 render_segments 表

```sql
CREATE TABLE render_segments (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  segment_index INTEGER NOT NULL,
  narration TEXT NOT NULL,
  visual_query TEXT NOT NULL,
  matched_clip TEXT,
  duration REAL,
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
| matched_clip | 匹配到的视频片段 |
| duration | 预计时长 |
| created_at | 创建时间 |

---

## 9. 核心任务流

### 9.1 一键生成视频流程

```text
1. 创建 render_task
2. 更新任务进度：10%，正在生成分镜
3. 调用 LLM 生成分镜 segments
4. 更新任务进度：30%，正在匹配素材
5. 调用 SentrySearch 匹配每个分镜的视频片段
6. 更新任务进度：50%，正在生成口播
7. 调用 edge-tts 生成 voice.mp3
8. 更新任务进度：65%，正在生成字幕
9. 根据 segments 生成 subtitle.srt
10. 更新任务进度：80%，正在合成视频
11. 调用 FFmpeg 裁剪、拼接、加字幕、加音频
12. 更新任务进度：100%，生成完成
```

### 9.2 后端伪代码

```python
def run_render_pipeline(task_id, req):
    update_task(task_id, 10, "正在生成分镜")
    segments = plan_script(req.script)

    update_task(task_id, 30, "正在匹配素材")
    segments = match_clips(segments)

    update_task(task_id, 50, "正在生成口播")
    voice_path = generate_tts(req.script, req.voice)

    update_task(task_id, 65, "正在生成字幕")
    subtitle_path = generate_subtitle(segments)

    update_task(task_id, 80, "正在合成视频")
    output_path = render_final_video(
        segments=segments,
        voice_path=voice_path,
        subtitle_path=subtitle_path,
        aspect_ratio=req.aspect_ratio
    )

    update_task(task_id, 100, "生成完成", output_path=output_path)
```

---

## 10. LLM 分镜 Prompt

```text
你是一个短视频分镜导演。

请把用户输入的口播文案拆成适合短视频混剪的分镜脚本。

要求：
1. 每个分镜包含 narration、visual_query、duration。
2. narration 是这一段要朗读的口播文本。
3. visual_query 是用于从视频素材库检索画面的描述，要具体、可视化。
4. duration 根据 narration 字数估算，中文每秒约 4～5 个字。
5. visual_query 要适合检索视频画面，不要太抽象。
6. 输出 JSON 数组，不要输出解释。

用户文案：
{{script}}

输出格式：
[
  {
    "narration": "现在很多企业都在做 AI Agent",
    "visual_query": "科技感办公室，AI大屏，团队讨论，企业数字化",
    "duration": 3.5
  }
]
```

---

## 11. FFmpeg 合成方案

### 11.1 统一竖屏 9:16

```bash
ffmpeg -i input.mp4 \
-vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
-an output_vertical.mp4
```

### 11.2 统一横屏 16:9

```bash
ffmpeg -i input.mp4 \
-vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080" \
-an output_horizontal.mp4
```

### 11.3 拼接片段

生成 `concat.txt`：

```text
file 'clip_001_vertical.mp4'
file 'clip_002_vertical.mp4'
file 'clip_003_vertical.mp4'
```

执行：

```bash
ffmpeg -f concat -safe 0 -i concat.txt -c copy output/bg.mp4
```

### 11.4 混入口播音频

```bash
ffmpeg -i output/bg.mp4 -i output/voice.mp3 \
-c:v copy -c:a aac -shortest output/with_voice.mp4
```

### 11.5 烧录字幕

```bash
ffmpeg -i output/with_voice.mp4 \
-vf "subtitles=output/subtitle.srt" \
-c:a copy output/final.mp4
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
  segments: any[];
}) {
  return api.post("/videos/match-clips", data);
}

export function renderVideo(data: {
  script: string;
  segments: any[];
  voice: string;
  aspect_ratio: string;
}) {
  return api.post("/videos/render", data);
}

export function getTask(taskId: string) {
  return api.get(`/tasks/${taskId}`);
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

### 阶段 1：跑通后端生成链路

目标：

```text
用一个接口 /api/videos/render 跑通完整生成流程。
```

任务：

```text
1. 初始化 FastAPI 项目
2. 配置静态文件目录
3. 实现 render_tasks 表
4. 实现任务创建和状态更新
5. 接入 LLM 分镜
6. 接入 SentrySearch 检索素材
7. 接入 edge-tts 生成口播
8. 接入 FFmpeg 合成视频
```

验收标准：

```text
输入一段文案，接口返回 task_id，最终 output/videos 生成 final.mp4。
```

---

### 阶段 2：跑通前端创建页面

目标：

```text
前端可以输入文案并生成视频。
```

任务：

```text
1. 初始化 Vue3 + Vite 项目
2. 安装 Element Plus
3. 创建 CreateVideo.vue
4. 封装 renderVideo 和 getTask API
5. 实现任务进度轮询
6. 实现视频预览
```

验收标准：

```text
前端点击“一键生成视频”，能看到进度，完成后能播放视频。
```

---

### 阶段 3：增加素材库页面

目标：

```text
支持前端上传素材和触发索引。
```

任务：

```text
1. 实现 /api/materials/upload
2. 实现 /api/materials
3. 实现 /api/materials/index
4. 前端实现 MaterialLibrary.vue
5. 支持素材列表展示
6. 支持上传和建索引按钮
```

验收标准：

```text
前端可以上传视频，后端保存到 materials 目录，并能触发索引。
```

---

### 阶段 4：增加分镜预览与手动调整

目标：

```text
用户可以看到 AI 生成的分镜，并查看匹配到的素材片段。
```

任务：

```text
1. 实现 /api/scripts/plan
2. 实现 /api/videos/match-clips
3. 前端展示分镜列表
4. 展示 matched_clip
5. 支持重新匹配单个分镜
```

验收标准：

```text
用户生成视频前，可以看到每句口播对应的视频画面。
```

---

### 阶段 5：优化生成效果

目标：

```text
让生成视频更像可发布短视频。
```

任务：

```text
1. 优化字幕样式
2. 增加背景音乐
3. 增加片段去重
4. 支持 9:16 / 16:9 / 1:1
5. 支持 top3 素材候选
6. 支持用户替换素材片段
```

验收标准：

```text
生成的视频画面不重复，字幕清晰，口播和画面节奏基本匹配。
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
