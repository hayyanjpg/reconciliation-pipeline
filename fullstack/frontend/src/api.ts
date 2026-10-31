import type {
  FileKey,
  Meta,
  ResultsResponse,
  Run,
  ValidationResponse,
} from "./types";

export const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  detail: unknown;

  constructor(message: string, detail: unknown) {
    super(message);
    this.name = "ApiError";
    this.detail = detail;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    let body: any = null;
    try {
      body = await response.json();
    } catch {
      body = null;
    }
    const detail = body?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : detail?.message ?? `Request gagal (${response.status})`;
    throw new ApiError(message, detail);
  }
  return (await response.json()) as T;
}

export function getMeta(): Promise<Meta> {
  return request<Meta>("/api/meta");
}

export function getRun(runId: string): Promise<Run> {
  return request<Run>(`/api/runs/${runId}`);
}

export function getResults(runId: string): Promise<ResultsResponse> {
  return request<ResultsResponse>(`/api/runs/${runId}/results`);
}

export function validateFiles(
  files: Partial<Record<FileKey, File | null>>,
): Promise<ValidationResponse> {
  const body = new FormData();
  (Object.keys(files) as FileKey[]).forEach((key) => {
    const file = files[key];
    if (file) body.append(key, file);
  });
  return request<ValidationResponse>("/api/validate", {
    method: "POST",
    body,
  });
}

export function createRun(
  asOf: string,
  files: Partial<Record<FileKey, File | null>>,
): Promise<{ id: string; status: string }> {
  const body = new FormData();
  body.append("as_of", asOf);
  (Object.keys(files) as FileKey[]).forEach((key) => {
    const file = files[key];
    if (file) body.append(key, file);
  });
  return request<{ id: string; status: string }>("/api/runs", {
    method: "POST",
    body,
  });
}

export function createDemoRun(
  asOf: string,
): Promise<{ id: string; status: string }> {
  const body = new FormData();
  body.append("as_of", asOf);
  return request<{ id: string; status: string }>("/api/runs/demo", {
    method: "POST",
    body,
  });
}

export function artifactUrl(runId: string, name: string): string {
  return `${API_BASE}/api/runs/${runId}/artifacts/${name}`;
}

export function templateUrl(key: FileKey | "all.zip"): string {
  if (key === "all.zip") return `${API_BASE}/api/templates/all.zip`;
  return `${API_BASE}/api/templates/${key}`;
}

export async function fetchCsv(url: string): Promise<string> {
  const response = await fetch(url);
  if (!response.ok) throw new ApiError("Gagal mengunduh data.", null);
  return response.text();
}


