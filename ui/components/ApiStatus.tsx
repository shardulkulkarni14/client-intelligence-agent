"use client";

import { useEffect, useState } from "react";
import { errorMessage } from "@/lib/errors";
import type { HealthResponse } from "@/lib/types";

type State = { kind: "loading" } | { kind: "up"; health: HealthResponse } | { kind: "down"; message: string };

/** One line in the header: is the Python service reachable, which model, is a key configured. */
export default function ApiStatus() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    fetch("/api/health")
      .then(async (res) => {
        const body = await res.json();
        if (!res.ok) setState({ kind: "down", message: errorMessage(body, res.status) });
        else setState({ kind: "up", health: body as HealthResponse });
      })
      .catch((e: Error) => setState({ kind: "down", message: e.message }));
  }, []);

  if (state.kind === "loading") return <span className="api-status muted small">Checking the API…</span>;
  if (state.kind === "down") {
    return (
      <span className="api-status small down" role="status" title={state.message}>
        <span className="dot" /> API not reachable. {state.message}
      </span>
    );
  }
  const { model, model_key_present: hasKey } = state.health;
  return (
    <span className="api-status small muted" role="status">
      <span className={hasKey ? "dot up" : "dot warn"} /> API reachable · model {model || "unknown"} ·{" "}
      {hasKey ? "model key configured" : "no model key configured"}
    </span>
  );
}
