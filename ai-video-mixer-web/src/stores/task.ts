import { defineStore } from "pinia";
import axios from "axios";
import { markRaw } from "vue";
import { getTask } from "@/api/task";
import type { Task } from "@/api/types";

const DONE = new Set(["completed", "failed"]);

export const useTaskStore = defineStore("task", {
  state: () => ({
    currentTask: null as Task | null,
    polling: 0 as number,
    pollController: null as AbortController | null,
  }),
  actions: {
    async load(taskId: string, signal?: AbortSignal) {
      this.currentTask = await getTask(taskId, signal);
      return this.currentTask;
    },
    startPolling(taskId: string, onDone?: (task: Task) => void, interval = 1500) {
      this.stopPolling();
      const poll = async () => {
        if (this.pollController) return;
        const controller = markRaw(new AbortController());
        this.pollController = controller;

        try {
          const task = await this.load(taskId, controller.signal);
          if (DONE.has(task.status)) {
            this.stopPolling();
            onDone?.(task);
          }
        } catch (error) {
          if (!axios.isCancel(error)) {
            console.error("Failed to poll task status", error);
          }
        } finally {
          if (this.pollController === controller) {
            this.pollController = null;
          }
        }
      };

      void poll();
      this.polling = window.setInterval(() => {
        void poll();
      }, interval);
    },
    stopPolling() {
      if (this.polling) {
        window.clearInterval(this.polling);
        this.polling = 0;
      }
      this.pollController?.abort();
      this.pollController = null;
    },
  },
});
