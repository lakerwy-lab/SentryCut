import { api } from "./client";
import type { AspectRatio, Segment } from "./types";

export async function planScript(data: {
  script: string;
  aspect_ratio: AspectRatio;
  voice: string;
}) {
  const res = await api.post<{ segments: Segment[] }>("/scripts/plan", data);
  return res.data.segments;
}

export async function matchClips(data: { segments: Segment[]; results?: number }) {
  const res = await api.post<{ segments: Segment[] }>("/videos/match-clips", data);
  return res.data.segments;
}

export async function renderVideo(data: {
  script: string;
  voice: string;
  aspect_ratio: AspectRatio;
  segments?: Segment[];
}) {
  const res = await api.post<{ task_id: string; type: "render"; status: string }>(
    "/videos/render",
    data,
  );
  return res.data;
}
