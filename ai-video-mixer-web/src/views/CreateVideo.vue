<template>
  <section>
    <header class="page-header">
      <div>
        <h2>创建视频</h2>
        <p>输入口播文案，生成分镜并匹配素材，一键合成带配音和字幕的 MP4。</p>
      </div>
      <el-button :icon="FolderOpened" @click="$router.push('/materials')">素材库</el-button>
    </header>

    <div class="workspace-grid">
      <div class="panel">
        <h3 class="panel-title">口播设置</h3>
        <el-form label-position="top">
          <el-form-item label="口播文案">
            <el-input
              v-model="script"
              type="textarea"
              :rows="10"
              resize="vertical"
              placeholder="请输入完整口播文案"
            />
          </el-form-item>
          <el-form-item label="视频比例">
            <el-segmented v-model="aspectRatio" :options="aspectOptions" />
          </el-form-item>
          <el-form-item label="配音音色">
            <el-select v-model="voice" style="width: 100%">
              <el-option label="中文女声-晓晓" value="zh-CN-XiaoxiaoNeural" />
              <el-option label="中文男声-云希" value="zh-CN-YunxiNeural" />
              <el-option label="中文男声-云健" value="zh-CN-YunjianNeural" />
              <el-option label="中文女声-晓伊" value="zh-CN-XiaoyiNeural" />
            </el-select>
          </el-form-item>
          <div class="toolbar">
            <el-button type="primary" :icon="DocumentChecked" :loading="planning" @click="handlePlan">
              生成分镜
            </el-button>
            <el-button :icon="Search" :loading="matching" :disabled="segments.length === 0" @click="handleMatch">
              匹配素材
            </el-button>
            <el-button type="success" :icon="VideoPlay" :loading="rendering" @click="handleRender">
              生成视频
            </el-button>
          </div>
        </el-form>

        <div v-if="taskStore.currentTask?.type === 'render'" class="status-line">
          <el-tag :type="taskStore.currentTask.status === 'failed' ? 'danger' : 'warning'">
            {{ taskStore.currentTask.status }}
          </el-tag>
          <el-progress :percentage="taskStore.currentTask.progress" style="width: 260px" />
          <span class="muted">{{ taskStore.currentTask.current_step }}</span>
        </div>
      </div>

      <div class="panel">
        <h3 class="panel-title">分镜预览</h3>
        <div v-if="segments.length === 0" class="empty-state">
          输入文案后生成分镜，匹配结果会显示在这里。
        </div>
        <div v-else class="segment-list">
          <article v-for="segment in segments" :key="segment.index" class="segment-item">
            <div class="segment-head">
              <strong>分镜 {{ segment.index }}</strong>
              <el-tag v-if="segment.similarity_score != null" type="success">
                {{ segment.similarity_score.toFixed(2) }}
              </el-tag>
            </div>
            <p><b>口播：</b>{{ segment.narration }}</p>
            <p><b>画面：</b>{{ segment.visual_query }}</p>
            <div class="metric-row">
              <el-tag type="info">{{ segment.estimated_duration ?? "-" }}s</el-tag>
              <el-tag v-if="segment.source_start_time != null" type="warning">
                {{ formatSeconds(segment.source_start_time) }} - {{ formatSeconds(segment.source_end_time) }}
              </el-tag>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { DocumentChecked, FolderOpened, Search, VideoPlay } from "@element-plus/icons-vue";
import { matchClips, planScript, renderVideo } from "@/api/video";
import type { AspectRatio, Segment, Task } from "@/api/types";
import { useTaskStore } from "@/stores/task";

const router = useRouter();
const taskStore = useTaskStore();
const script = ref("");
const voice = ref("zh-CN-XiaoxiaoNeural");
const aspectRatio = ref<AspectRatio>("9:16");
const aspectOptions = ["9:16", "16:9", "1:1"];
const segments = ref<Segment[]>([]);
const planning = ref(false);
const matching = ref(false);
const rendering = ref(false);

function formatSeconds(value?: number | null) {
  if (value == null) return "-";
  const m = Math.floor(value / 60);
  const s = Math.round(value % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

function requireScript() {
  if (!script.value.trim()) {
    ElMessage.warning("请先输入口播文案");
    return false;
  }
  return true;
}

async function handlePlan() {
  if (!requireScript()) return;
  planning.value = true;
  try {
    segments.value = await planScript({
      script: script.value,
      aspect_ratio: aspectRatio.value,
      voice: voice.value,
    });
    ElMessage.success("分镜已生成");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "生成分镜失败");
  } finally {
    planning.value = false;
  }
}

async function handleMatch() {
  if (segments.value.length === 0) return;
  matching.value = true;
  try {
    segments.value = await matchClips({ segments: segments.value, results: 1 });
    ElMessage.success("素材匹配完成");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "匹配失败");
  } finally {
    matching.value = false;
  }
}

async function handleRender() {
  if (!requireScript()) return;
  rendering.value = true;
  try {
    const task = await renderVideo({
      script: script.value,
      voice: voice.value,
      aspect_ratio: aspectRatio.value,
      segments: segments.value,
    });
    taskStore.startPolling(task.task_id, (done: Task) => {
      rendering.value = false;
      if (done.status === "completed") {
        ElMessage.success("视频生成完成");
        void router.push(`/preview/${done.task_id}`);
      } else if (done.status === "failed") {
        ElMessage.error(done.error_message || "生成失败");
      }
    });
    void router.push(`/tasks/${task.task_id}`);
  } catch (error) {
    rendering.value = false;
    ElMessage.error(error instanceof Error ? error.message : "生成视频失败");
  }
}
</script>
