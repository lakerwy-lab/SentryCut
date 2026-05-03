import { api } from "./client";
import type { Material } from "./types";

export async function uploadMaterial(file: File) {
  const data = new FormData();
  data.append("file", file);
  const res = await api.post<Material>("/materials/upload", data, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function listMaterials() {
  const res = await api.get<{ items: Material[] }>("/materials");
  return res.data.items;
}

export async function indexMaterials(materialIds: string[]) {
  const res = await api.post<{ task_id: string; type: "index"; status: string }>(
    "/materials/index",
    { material_ids: materialIds },
  );
  return res.data;
}

export async function deleteMaterial(materialId: string) {
  const res = await api.delete<{ material_id: string; removed_chunks: number }>(
    `/materials/${materialId}`,
  );
  return res.data;
}
