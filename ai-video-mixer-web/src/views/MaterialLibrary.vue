<template>
  <section>
    <header class="page-header">
      <div>
        <h2>素材库</h2>
        <p>上传视频素材，建立 SentrySearch 索引后即可用于自动匹配。</p>
      </div>
      <el-button :icon="Refresh" @click="loadMaterials" :loading="loading">刷新</el-button>
    </header>

    <div class="panel">
      <div class="toolbar">
        <el-upload
          :auto-upload="false"
          :show-file-list="false"
          multiple
          accept=".mp4,.mov,video/mp4,video/quicktime"
          :on-change="handleFile"
        >
          <el-button type="primary" :icon="Upload" :loading="uploading">上传视频</el-button>
        </el-upload>
        <el-button
          type="success"
          :icon="Connection"
          :disabled="selectedIds.length === 0"
          @click="startIndex"
        >
          建立索引
        </el-button>
        <span class="muted">已选 {{ selectedIds.length }} 个素材</span>
      </div>

      <div v-if="taskStore.currentTask?.type === 'index'" class="status-line">
        <el-tag :type="taskTagType(taskStore.currentTask.status)">
          {{ taskStore.currentTask.status }}
        </el-tag>
        <el-progress :percentage="taskStore.currentTask.progress" style="width: 260px" />
        <span class="muted">{{ taskStore.currentTask.current_step }}</span>
      </div>

      <el-table
        v-loading="loading"
        :data="materials"
        row-key="id"
        style="width: 100%; margin-top: 18px"
        @selection-change="handleSelection"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column prop="original_filename" label="文件名" min-width="190" />
        <el-table-column label="时长" width="96">
          <template #default="{ row }">{{ formatSeconds(row.duration) }}</template>
        </el-table-column>
        <el-table-column label="规格" width="140">
          <template #default="{ row }">
            <span v-if="row.width && row.height">{{ row.width }}x{{ row.height }}</span>
            <span v-else class="muted">未知</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="materialTagType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="embedding_backend" label="后端" width="110" />
        <el-table-column label="路径" min-width="220">
          <template #default="{ row }">
            <el-text truncated>{{ row.path }}</el-text>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="104" fixed="right">
          <template #default="{ row }">
            <el-button
              type="danger"
              link
              :icon="Delete"
              :disabled="row.status === 'indexing'"
              :loading="deletingId === row.id"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { ElMessage, ElMessageBox, type UploadFile } from "element-plus";
import { Connection, Delete, Refresh, Upload } from "@element-plus/icons-vue";
import { deleteMaterial, indexMaterials, listMaterials, uploadMaterial } from "@/api/material";
import type { Material, Task } from "@/api/types";
import { useTaskStore } from "@/stores/task";

const materials = ref<Material[]>([]);
const loading = ref(false);
const uploadingCount = ref(0);
const uploading = computed(() => uploadingCount.value > 0);
const deletingId = ref("");
const selectedIds = ref<string[]>([]);
const taskStore = useTaskStore();

function formatSeconds(value: number | null) {
  if (value == null) return "未知";
  const m = Math.floor(value / 60);
  const s = Math.round(value % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

function materialTagType(status: string) {
  if (status === "indexed") return "success";
  if (status === "failed") return "danger";
  if (status === "indexing") return "warning";
  return "info";
}

function taskTagType(status: string) {
  if (status === "completed") return "success";
  if (status === "failed") return "danger";
  return "warning";
}

async function loadMaterials() {
  loading.value = true;
  try {
    materials.value = await listMaterials();
  } finally {
    loading.value = false;
  }
}

async function handleFile(upload: UploadFile) {
  if (!upload.raw) return;
  uploadingCount.value += 1;
  try {
    await uploadMaterial(upload.raw);
    ElMessage.success("素材已上传");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "上传失败");
  } finally {
    uploadingCount.value = Math.max(0, uploadingCount.value - 1);
    if (uploadingCount.value === 0) {
      await loadMaterials();
    }
  }
}

function handleSelection(rows: Material[]) {
  selectedIds.value = rows.map((row) => row.id);
}

async function startIndex() {
  const task = await indexMaterials(selectedIds.value);
  taskStore.startPolling(task.task_id, async (done: Task) => {
    await loadMaterials();
    if (done.status === "completed") ElMessage.success("索引完成");
    if (done.status === "failed") ElMessage.error(done.error_message || "索引失败");
  });
}

async function handleDelete(material: Material) {
  try {
    await ElMessageBox.confirm(
      `确定删除「${material.original_filename}」吗？已建立的索引片段也会一起清理。`,
      "删除素材",
      {
        type: "warning",
        confirmButtonText: "删除",
        cancelButtonText: "取消",
      },
    );
  } catch {
    return;
  }

  deletingId.value = material.id;
  try {
    const result = await deleteMaterial(material.id);
    selectedIds.value = selectedIds.value.filter((id) => id !== material.id);
    ElMessage.success(`已删除素材，清理 ${result.removed_chunks} 个索引片段`);
    await loadMaterials();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "删除失败");
  } finally {
    deletingId.value = "";
  }
}

onMounted(loadMaterials);
</script>
