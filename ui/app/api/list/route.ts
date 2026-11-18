import { NextResponse } from "next/server";
import { runCli, stderrTail } from "@/lib/cli";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const res = await runCli(["--list"]);
  if (res.exitCode !== 0 || res.json === null) {
    return NextResponse.json(
      { error: `client-intel --list failed (exit ${res.exitCode}): ${stderrTail(res.stderr)}` },
      { status: 502 },
    );
  }
  return NextResponse.json(res.json);
}
