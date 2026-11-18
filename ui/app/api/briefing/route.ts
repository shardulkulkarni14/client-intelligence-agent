import { NextResponse } from "next/server";
import { runCli, stderrTail } from "@/lib/cli";
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
  const client = typeof body.client === "string" ? body.client.trim() : "";
  const trigger = typeof body.trigger === "string" ? body.trigger : "";
  const context = typeof body.context === "string" ? body.context.trim() : "";
  // Anything but an explicit true runs without the model, so a malformed request is never a paid one.
  const useModel = body.useModel === true;

  if (!CLIENT_RE.test(client)) return bad(400, "Client must be 1 to 80 letters, digits, spaces or . , & ' ( ) -");
  if (context.length > MAX_CONTEXT) return bad(400, `Context must be at most ${MAX_CONTEXT} characters.`);

  const list = await runCli(["--list"]);
  if (list.exitCode !== 0 || list.json === null) {
    return bad(502, `Could not read the trigger list (exit ${list.exitCode}): ${stderrTail(list.stderr)}`);
  }
  const triggers = ((list.json as ListResponse).triggers ?? []).map((t) => t.name);
  if (!triggers.includes(trigger)) return bad(400, `Trigger must be one of: ${triggers.join(", ")}`);

  if (busy) return bad(409, "A briefing is already being written. Wait for it to finish.");
  busy = true;
  try {
    // "--flag=value" keeps a value that starts with a dash from being read as another option.
    const args = [`--client=${client}`, `--trigger=${trigger}`, "--json"];
    if (context) args.push(`--context=${context}`);
    if (!useModel) args.push("--no-llm");
    const res = await runCli(args);
    if (res.json === null) {
      return bad(502, `client-intel printed no JSON (exit ${res.exitCode}): ${stderrTail(res.stderr)}`);
    }
    const ok = (res.json as { ok?: boolean }).ok === true;
    return NextResponse.json(res.json, { status: ok ? 200 : 422 });
  } finally {
    busy = false;
  }
}
