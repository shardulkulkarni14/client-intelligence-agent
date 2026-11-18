import { callApi, passThrough } from "@/lib/api";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return passThrough(await callApi("/api/meta"));
}
