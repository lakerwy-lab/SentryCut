import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
  timeout: 30_000,
});

export const staticUrl = (path?: string | null) => {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  return path;
};
