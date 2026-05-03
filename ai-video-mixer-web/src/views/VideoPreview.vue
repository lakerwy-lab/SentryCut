<template>
  <section>
    <header class="page-header">
      <div>
        <h2>视频预览</h2>
        <p>{{ taskId }}</p>
      </div>
      <div class="toolbar">
        <el-button :icon="Refresh" @click="loadTask">刷新</el-button>
        <el-button :icon="Back" @click="$router.push('/create')">重新生成</el-button>
      </div>
    </header>

    <div class="panel">
      <div v-if="task?.status !== 'completed'" class="empty-state">
        <div>
          <p>视频还没有生成完成。</p>
          <el-button type="primary" @click="$router.push(`/tasks/${taskId}`)">查看任务</el-button>
        </div>
      </div>

      <template v-else>
        <video class="video-frame" :src="task.output_url || ''" controls />
        <div class="toolbar" style="margin-top: 16px">
          <el-button
            v-if="task.output_url"
            type="primary"
            :icon="Download"
            tag="a"
            :href="task.output_url"
            download
          >
            下载 MP4
          </el-button>
          <el-button
            v-if="task.subtitle_url"
            :icon="Document"
            tag="a"
            :href="task.subtitle_url"
            download
          >
            下载字幕
          </el-button>
        </div>
      </template>
    </div>

    <div v-if="segments.length" class="panel" style="margin-top: 18px">
      <h3 class="panel-title">使用的素材片段</h3>
      <div class="segment-list">
        <article v-for="segment in segments" :key="segment.index" class="segment-item">
          <div class="segment-head">
            <strong>分镜 {{ segment.index }}</strong>
            <el-tag v-if="segment.similarity_score != null" type="success">
              {{ segment.similarity_score.toFixed(2) }}
            </el-tag>
          </div>
          <p><b>口播：</b>{{ segment.narration }}</p>
          <p><b>素材：</b>{{ segment.source_file }}</p>
          <div class="metric-row">
            <el-tag>{{ segment.source_start_time }}s - {{ segment.source_end_time }}s</el-tag>
            <el-tag type="info">实际 {{ segment.actual_duration }}s</el-tag>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { Back, Document, Download, Refresh } from "@element-plus/icons-vue";
import { useTaskStore } from "@/stores/task";

const props = defineProps<{ taskId: string }>();
const taskStore = useTaskStore();
const task = computed(() => taskStore.currentTask);
const segments = computed(() => task.value?.result_json?.segments ?? []);

async function loadTask() {
  await taskStore.load(props.taskId);
}

onMounted(loadTask);
</script>
