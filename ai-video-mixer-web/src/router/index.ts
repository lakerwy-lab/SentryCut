import { createRouter, createWebHistory } from "vue-router";
import MaterialLibrary from "@/views/MaterialLibrary.vue";
import CreateVideo from "@/views/CreateVideo.vue";
import TaskDetail from "@/views/TaskDetail.vue";
import VideoPreview from "@/views/VideoPreview.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/materials" },
    { path: "/materials", component: MaterialLibrary },
    { path: "/create", component: CreateVideo },
    { path: "/tasks/:taskId", component: TaskDetail, props: true },
    { path: "/preview/:taskId", component: VideoPreview, props: true },
  ],
});

export default router;
