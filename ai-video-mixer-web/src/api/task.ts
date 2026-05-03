import { api } from "./client";
import type { Task } from "./types";

export async function getTask(taskId: string, signal?: AbortSignal) {
  const res = await api.get<Task>(`/tasks/${taskId}`, { signal });
  return res.data;
}
