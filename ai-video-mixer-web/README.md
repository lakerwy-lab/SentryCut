# AI 视频素材混剪助手 - 前端

Vue3 + Vite + TypeScript + Element Plus + Axios + Vue Router + Pinia。

已完成阶段 3 的前端 MVP：

- 素材库页：上传 mp4 / mov、查看素材列表、选择素材建立索引、轮询索引任务
- 创建视频页：输入口播文案、选择比例和音色、生成分镜、匹配素材、一键生成视频
- 任务详情页：查看 index/render 任务状态、进度、错误和渲染分镜
- 视频预览页：播放生成 MP4、下载 MP4 和 SRT、查看使用的素材片段

## 启动

先启动后端：

```powershell
cd ai-video-mixer-api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

再启动前端：

```powershell
cd ai-video-mixer-web
npm install
npm run dev
```

访问：

```text
http://localhost:5173
```

Vite 会把 `/api` 和 `/static` 代理到 `http://127.0.0.1:8000`。

## 构建

```powershell
npm run build
```

## 页面

```text
/materials           素材库
/create              创建视频
/tasks/:taskId       任务详情
/preview/:taskId     视频预览
```

## 下一步

- 分镜结果支持单段重新匹配
- 每个分镜返回 top3 候选并允许替换
- 优化字幕样式和 BGM
