/**
 * Minimal fetch wrapper for the ANIF platform API.
 *
 * Base URL defaults to /api — the vite dev server proxies this to the
 * backend (see vite.config.ts). The X-API-Key header is the B-track
 * placeholder auth until X.509 gateway wiring lands.
 */

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "/api";
const API_KEY: string = import.meta.env.VITE_ANIF_API_KEY ?? "";

export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : `API request failed (HTTP ${status})`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

interface RequestOptions {
  method?: "GET" | "POST";
  body?: unknown;
  params?: Record<string, string | number | undefined>;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const url = new URL(BASE_URL + path, window.location.origin);
  for (const [key, value] of Object.entries(options.params ?? {})) {
    if (value !== undefined) url.searchParams.set(key, String(value));
  }

  const response = await fetch(url, {
    method: options.method ?? "GET",
    headers: {
      "X-API-Key": API_KEY,
      ...(options.body !== undefined ? { "Content-Type": "application/json" } : {}),
    },
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  let payload: unknown = null;
  const text = await response.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!response.ok) {
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? (payload as { detail: unknown }).detail
        : payload;
    throw new ApiError(response.status, detail);
  }

  return payload as T;
}
