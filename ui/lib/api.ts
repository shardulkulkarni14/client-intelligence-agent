import { NextResponse } from "next/server";

// Server-side only: the browser talks to the Next routes, never to the service directly,
// so the service address stays here and no CORS setup is needed.
const BASE_URL = (process.env.CLIENT_INTEL_API_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");

export const UNREACHABLE = "The client-intel API is not running. Start it with: uv run client-intel-api";

export const BRIEFING_TIMEOUT_MS = 180_000;
export const DEFAULT_TIMEOUT_MS = 30_000;

export interface ApiResult {
  status: number;
  json: unknown;
}

interface CallOptions {
  method?: "GET" | "POST";
  body?: unknown;
  timeoutMs?: number;
}

function failure(status: number, error: string): ApiResult {
  return { status, json: { ok: false, error } };
}

/** Calls the service and returns its status code and JSON body; never throws. */
export async function callApi(path: string, options: CallOptions = {}): Promise<ApiResult> {
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: options.method ?? "GET",
      headers: options.body === undefined ? undefined : { "content-type": "application/json" },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      cache: "no-store",
      signal: controller.signal,
    });
    const text = await res.text();
    try {
      return { status: res.status, json: JSON.parse(text) };
    } catch {
      return failure(502, `The client-intel API answered ${path} with HTTP ${res.status} and no JSON.`);
    }
  } catch {
    // An abort is our own timeout; anything else (refused, reset, DNS) means nothing is listening.
    if (controller.signal.aborted) {
      return failure(504, `The client-intel API did not answer ${path} within ${timeoutMs / 1000} s.`);
    }
    return failure(503, UNREACHABLE);
  } finally {
    clearTimeout(timer);
  }
}

/** Passes the service's status code and JSON body through unchanged. */
export function passThrough(result: ApiResult): NextResponse {
  return NextResponse.json(result.json, { status: result.status });
}
