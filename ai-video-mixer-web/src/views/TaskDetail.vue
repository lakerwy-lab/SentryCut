<template>
  <section>
    <header class="page-header">
      <div>
        <h2>任务详情</h2>
        <p>{{ taskId }}</p>
      </div>
      <div class="toolbar">
        <el-button :icon="Refresh" @click="loadTask">刷新</el-button>
        <el-button
          v-if="task?.status === 'completed' && task.type === 'render'"
          type="primary"
          :icon="View"
          @click="$router.push(`/preview/${task.task_id}`)"
        >
          查看视频
        </el-button>
      </div>
    </header>

    <div class="workspace-grid">
      <div class="panel">
        <h3 class="panel-title">进度</h3>
        <div v-if="!task" class="empty-state">正在加载任务</div>
        <template v-else>
          <div class="status-line">
            <el-tag :type="tagType(task.status)">{{ task.type }}</el-tag>
            <el-tag :type="tagType(task.status)">{{ task.status }}</el-tag>
          </div>
          <el-progress :percentage="task.progress" style="margin-top: 18px" />
          <p class="muted">{{ task.current_step }}</p>
          <el-alert
            v-if="task.error_message"
            type="error"
            :title="task.error_message"
            show-icon
            :closable="false"
          />
        </template>
      </div>

      <div class="panel">
        <h3 class="panel-title">结果</h3>
        <div v-if="!task?.result_json" class="empty-state">任务完成后会显示输出结果。</div>
        <template v-else>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="输出视频">
              <el-link v-if="task.output_url" :href="task.output_url" target="_blank">
                {{ task.output_url }}
              </el-link>
              <span v-else class="muted">无</span>
            </el-descriptions-item>
            <el-descriptions-item label="字幕文件">
              <el-link v-if="task.subtitle_url" :href="task.subtitle_url" target="_blank">
                {{ task.subtitle_url }}
              </el-link>
              <span v-else class="muted">无</span>
            </el-descriptions-item>
          </el-descriptions>
        </template>
      </div>
    </div>

    <div v-if="segments.length" class="panel" style="margin-top: 18px">
      <h3 class="panel-title">分镜记录</h3>
      <el-table :data="segments" style="width: 100%">
        <el-table-column prop="index" label="#" width="64" />
        <el-table-column prop="narration" label="口播" min-width="220" />
        <el-table-column prop="visual_query" label="画面检索" min-width="240" />
        <el-table-column label="时长" width="100">
          <template #default="{ row }">{{ row.actual_duration ?? row.estimated_duration }}s</template>
        </el-table-column>
        <el-table-column label="相似度" width="100">
          <template #default="{ row }">
            {{ row.similarity_score == null ? "-" : row.similarity_score.toFixed(2) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from "vue";
import { Refresh, View } from "@element-plus/icons-vue";
import { useTaskStore } from "@/stores/task";

const props = defineProps<{ taskId: string }>();
const taskStore = useTaskStore();
const task = computed(() => taskStore.currentTask);
const segments = computed(() => task.value?.result_json?.segments ?? []);

function tagType(status: string) {
  if (status === "completed") return "success";
  if (status === "failed") return "danger";
  return "warning";
}

async function loadTask() {
  await taskStore.load(props.taskId);
}

onMounted(() => {
  taskStore.startPolling(props.taskId);
});

onUnmounted(() => {
  taskStore.stopPolling();
});
</script>
