/** Best message from an error body: ours and the service's use `error`, FastAPI's own use `detail`. */
export function errorMessage(body: unknown, status: number): string {
  const b = (body ?? {}) as { error?: unknown; detail?: unknown };
  if (typeof b.error === "string" && b.error) return b.error;
  if (typeof b.detail === "string" && b.detail) return b.detail;
  if (b.detail !== undefined) return `HTTP ${status}: ${JSON.stringify(b.detail).slice(0, 500)}`;
  return `HTTP ${status}`;
}
