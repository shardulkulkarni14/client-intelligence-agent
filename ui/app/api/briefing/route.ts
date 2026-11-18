import { NextResponse } from "next/server";
import { BRIEFING_TIMEOUT_MS, callApi, passThrough } from "@/lib/api";
import type { ListResponse } from "@/lib/types";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const CLIENT_RE = /^[\w .,&'()-]{1,80}$/;
const MAX_CONTEXT = 500;

// A model run costs money and takes about 40 s; a second click must not start a second one.
let busy = false;

function bad(status: number, error: string) {
  return NextResponse.json({ ok: false, error }, { status });
}

export async function POST(request: Request) {
  let body: Record<string, unknown>;
  try {
    body = (await request.json()) as Record<string, unknown>;
  } catch {
    return bad(400, "Request body must be JSON.");
  }
  if (body === null || typeof body !== "object") return bad(400, "Request body must be a JSON object.");
  const client = typeof body.client === "string" ? body.client.trim() : "";
  const trigger = typeof body.trigger === "string" ? body.trigger : "";
  const context = typeof body.context === "string" ? body.context.trim() : "";
  // Anything but an explicit true runs without the model, so a malformed request is never a paid one.
  const useModel = body.useModel === true;

  if (!CLIENT_RE.test(client)) return bad(400, "Client must be 1 to 80 letters, digits, spaces or . , & ' ( ) -");
  if (context.length > MAX_CONTEXT) return bad(400, `Context must be at most ${MAX_CONTEXT} characters.`);

  const meta = await callApi("/api/meta");
  if (meta.status !== 200) return passThrough(meta);
  const triggers = ((meta.json as ListResponse).triggers ?? []).map((t) => t.name);
  if (!triggers.includes(trigger)) return bad(400, `Trigger must be one of: ${triggers.join(", ")}`);

  if (busy) return bad(409, "A briefing is already being written. Wait for it to finish.");
  busy = true;
  try {
    const result = await callApi("/api/briefings", {
      method: "POST",
      body: { client, trigger, context, use_model: useModel },
      timeoutMs: BRIEFING_TIMEOUT_MS,
    });
    return passThrough(result);
  } finally {
    busy = false;
  }
}
