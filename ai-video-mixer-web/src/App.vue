<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">AI</div>
        <div>
          <h1>视频混剪助手</h1>
          <p>素材检索与自动合成</p>
        </div>
      </div>

      <nav class="nav">
        <RouterLink to="/materials">
          <el-icon><FolderOpened /></el-icon>
          <span>素材库</span>
        </RouterLink>
        <RouterLink to="/create">
          <el-icon><VideoPlay /></el-icon>
          <span>创建视频</span>
        </RouterLink>
      </nav>
    </aside>

    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { FolderOpened, VideoPlay } from "@element-plus/icons-vue";
</script>
