"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import BriefingView from "@/components/BriefingView";
import { errorMessage } from "@/lib/errors";
import type { BriefingResponse, HealthResponse, ListResponse } from "@/lib/types";

const MAX_CONTEXT = 500;

function BriefingPage() {
  const preselected = useSearchParams().get("client") ?? "";
  const [list, setList] = useState<ListResponse | null>(null);
  const [client, setClient] = useState("");
  const [trigger, setTrigger] = useState("");
  const [context, setContext] = useState("");
  const [useModel, setUseModel] = useState(true);
  const [noKey, setNoKey] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BriefingResponse | null>(null);

  useEffect(() => {
    fetch("/api/list")
      .then(async (res) => {
        const body = await res.json();
        if (!res.ok) throw new Error(errorMessage(body, res.status));
        const data = body as ListResponse;
        setList(data);
        const wanted = data.clients.find((c) => c.client_id === preselected);
        setClient((wanted ?? data.clients[0])?.client_id ?? "");
        setTrigger(data.triggers[0]?.name ?? "");
      })
      .catch((e: Error) => setError(`Could not load clients and triggers. ${e.message}`));
  }, [preselected]);

  useEffect(() => {
    // Without a key a model run can only fail, so the box starts unticked. Best effort:
    // if the health check itself fails, the header already says the API is down.
    fetch("/api/health")
      .then(async (res) => {
        if (!res.ok) return;
        const health = (await res.json()) as HealthResponse;
        if (health.model_key_present === false) {
          setNoKey(true);
          setUseModel(false);
        }
      })
      .catch(() => undefined);
  }, []);

  async function run() {
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/briefing", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ client, trigger, context, useModel }),
      });
      const body = (await res.json()) as BriefingResponse;
      if (!res.ok || !body.ok) setError(errorMessage(body, res.status));
      else setResult(body);
    } catch (e) {
      setError(`The run failed. ${(e as Error).message}`);
    } finally {
      setRunning(false);
    }
  }

  const question = list?.triggers.find((t) => t.name === trigger)?.question;

  return (
    <>
      <form
        className="controls"
        onSubmit={(e) => {
          e.preventDefault();
          void run();
        }}
      >
        <label>
          Client
          <select value={client} onChange={(e) => setClient(e.target.value)} disabled={!list}>
            {(list?.clients ?? []).map((c) => (
              <option key={c.client_id} value={c.client_id}>
                {c.client_name} ({c.client_id}), {c.segment}, {c.tier}
              </option>
            ))}
          </select>
        </label>
        <label>
          Trigger
          <select value={trigger} onChange={(e) => setTrigger(e.target.value)} disabled={!list}>
            {(list?.triggers ?? []).map((t) => (
              <option key={t.name} value={t.name}>
                {t.name}
              </option>
            ))}
          </select>
        </label>
        <label className="wide">
          Context from the rep (optional)
          <textarea
            value={context}
            maxLength={MAX_CONTEXT}
            rows={2}
            onChange={(e) => setContext(e.target.value)}
            placeholder="For example: meeting with their head of trading on Thursday"
          />
        </label>
        <label className="check">
          <input type="checkbox" checked={useModel} onChange={(e) => setUseModel(e.target.checked)} />
          Use the model
          <span className="muted small">
            {useModel ? "(written briefing, about 40 seconds, costs a few cents)" : "(facts only, free, instant)"}
          </span>
          {noKey ? (
            <span className="small nokey">
              Off by default: the API reports that no model key is configured, so a model run would fail.
            </span>
          ) : null}
        </label>
        <button type="submit" className="primary" disabled={running || !client || !trigger}>
          {running ? "Working…" : "Run"}
        </button>
      </form>

      {question ? <p className="muted small question">Question for this trigger: {question}</p> : null}
      {list ? <p className="muted small">Data as of {list.as_of}.</p> : null}

      {running ? (
        <p className="working" role="status">
          <span className="spinner" /> Working, about {useModel ? "40 seconds" : "2 seconds"}. The tools run,{" "}
          {useModel ? "the model writes, " : ""}then the text is checked against the evidence.
        </p>
      ) : null}
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {result ? <BriefingView result={result} /> : null}
    </>
  );
}

export default function Page() {
  // useSearchParams needs a Suspense boundary for the static build.
  return (
    <Suspense fallback={<p className="muted">Loading…</p>}>
      <BriefingPage />
    </Suspense>
  );
}
