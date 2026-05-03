export type AspectRatio = "9:16" | "16:9" | "1:1";
export type TaskType = "index" | "render";

export interface Material {
  id: string;
  original_filename: string;
  stored_filename: string;
  path: string;
  duration: number | null;
  width: number | null;
  height: number | null;
  fps: number | null;
  status: string;
  embedding_backend: string | null;
  embedding_model: string | null;
  index_error: string | null;
  created_at: string;
}

export interface Segment {
  index: number;
  narration: string;
  visual_query: string;
  estimated_duration?: number | null;
  actual_duration?: number | null;
  source_file?: string | null;
  source_start_time?: number | null;
  source_end_time?: number | null;
  similarity_score?: number | null;
  matched_clip?: string | null;
  clip_path?: string | null;
  voice_path?: string | null;
  subtitle_start?: number | null;
  subtitle_end?: number | null;
}

export interface Task {
  task_id: string;
  type: TaskType;
  status: string;
  progress: number;
  current_step: string | null;
  output_url: string | null;
  subtitle_url: string | null;
  error_message: string | null;
  result_json: {
    output_url?: string;
    subtitle_url?: string;
    segments?: Segment[];
    indexed_count?: number;
    failed_count?: number;
    stats?: unknown;
  } | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}
