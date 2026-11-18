"use client";

import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CITE_HREF, FLAG_HREF, KIND_LABEL, lookupCitation, markCitations } from "@/lib/evidence";
import type { BriefingResponse, Fact, Gap, TraceStep } from "@/lib/types";

function num(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

/** Token and cost fields may sit on the step or inside its detail object; accept both. */
function stepNumber(step: TraceStep, key: string): number | null {
  const direct = num(step[key]);
  if (direct !== null) return direct;
  if (step.detail && typeof step.detail === "object") {
    return num((step.detail as Record<string, unknown>)[key]);
  }
  return null;
}

function stepTokens(step: TraceStep): { input: number | null; output: number | null } {
  return { input: stepNumber(step, "input_tokens"), output: stepNumber(step, "output_tokens") };
}

const SHOWN_ELSEWHERE = new Set(["input_tokens", "output_tokens", "cost_usd"]);

function detailText(detail: unknown): string {
  if (detail === null || detail === undefined) return "";
  if (typeof detail !== "object") return String(detail);
  return Object.entries(detail as Record<string, unknown>)
    .filter(([key, value]) => !SHOWN_ELSEWHERE.has(key) && value !== null)
    .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : typeof value === "object" ? JSON.stringify(value) : String(value)}`)
    .join("; ");
}

function Rows({ rows }: { rows: string[] | undefined }) {
  if (!rows || rows.length === 0) return <p className="muted small">No source rows recorded.</p>;
  return (
    <p className="small">
      <span className="muted">Source rows: </span>
      {rows.map((row) => (
        <code key={row} className="row">
          {row}
        </code>
      ))}
    </p>
  );
}

function FactCard({ fact, tool }: { fact: Fact; tool: string }) {
  return (
    <div className="card">
      <p>{fact.text}</p>
      <p className="small">
        <span className={`kind kind-${fact.kind}`}>{KIND_LABEL[fact.kind] ?? fact.kind}</span>
        <span className="muted"> from {tool}</span>
        {fact.id ? <code className="row">{fact.id}</code> : null}
      </p>
      <Rows rows={fact.rows} />
    </div>
  );
}

function GapCard({ gap }: { gap: Gap }) {
  return (
    <div className="card">
      <p>{gap.text}</p>
      <p className="small">
        <span className="kind kind-gap">{KIND_LABEL.gap}</span>
        <span className="muted"> {gap.code}</span>
      </p>
      <Rows rows={gap.rows} />
    </div>
  );
}

export default function BriefingView({ result }: { result: BriefingResponse }) {
  const [selected, setSelected] = useState<string | null>(null);
  const evidence = result.evidence;
  const marked = useMemo(() => markCitations(result.briefing ?? ""), [result.briefing]);
  const found = useMemo(
    () => (selected ? lookupCitation(evidence, selected) : null),
    [evidence, selected],
  );

  const final = evidence?.verification?.final;
  const trace = evidence?.trace;
  const steps = trace?.steps ?? [];
  const totalIn = steps.reduce((sum, s) => sum + (stepTokens(s).input ?? 0), 0);
  const totalOut = steps.reduce((sum, s) => sum + (stepTokens(s).output ?? 0), 0);
  const flagged = result.flagged ?? final?.violations?.length ?? 0;

  return (
    <div className={found ? "result with-panel" : "result"}>
      <section className="briefing">
        <p className={flagged > 0 ? "verify warn" : "verify"}>
          Verification: {final?.numbers_checked ?? "?"} numbers checked,{" "}
          {final?.citations_checked ?? "?"} citations checked, {flagged} flagged,{" "}
          {result.repaired ? "repaired once" : "no repair needed"}
          {evidence?.writer?.mode ? ` (writer: ${evidence.writer.mode})` : ""}
        </p>

        <article className="markdown">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              a({ href, children }) {
                if (href?.startsWith(CITE_HREF)) {
                  const id = decodeURIComponent(href.slice(CITE_HREF.length));
                  return (
                    <button
                      type="button"
                      className={id === selected ? "chip active" : "chip"}
                      onClick={() => setSelected(id === selected ? null : id)}
                      title="Show the evidence for this citation"
                    >
                      {id}
                    </button>
                  );
                }
                if (href === FLAG_HREF) {
                  return <span className="flag">Unverified: {children}</span>;
                }
                return (
                  <a href={href} target="_blank" rel="noreferrer">
                    {children}
                  </a>
                );
              },
            }}
          >
            {marked}
          </ReactMarkdown>
        </article>

        {trace ? (
          <details>
            <summary>
              Run trace{trace.model ? ` (${trace.model})` : ""}
              {num(trace.total_seconds) !== null ? `, ${trace.total_seconds!.toFixed(1)} s` : ""}
            </summary>
            <table>
              <thead>
                <tr>
                  <th>Step</th>
                  <th>Kind</th>
                  <th className="n">Seconds</th>
                  <th className="n">Tokens in / out</th>
                  <th className="n">Cost (USD)</th>
                  <th>Detail</th>
                </tr>
              </thead>
              <tbody>
                {steps.map((step, i) => {
                  const tokens = stepTokens(step);
                  const cost = stepNumber(step, "cost_usd");
                  return (
                    <tr key={`${step.name}-${i}`}>
                      <td>{step.name}</td>
                      <td>{step.kind}</td>
                      <td className="n">{num(step.seconds)?.toFixed(3) ?? ""}</td>
                      <td className="n">
                        {tokens.input !== null || tokens.output !== null
                          ? `${tokens.input ?? 0} / ${tokens.output ?? 0}`
                          : ""}
                      </td>
                      <td className="n">{cost !== null ? cost.toFixed(4) : ""}</td>
                      <td className="small muted detail">{detailText(step.detail)}</td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr>
                  <td colSpan={2}>Total</td>
                  <td className="n">{num(trace.total_seconds)?.toFixed(2) ?? ""}</td>
                  <td className="n">{totalIn || totalOut ? `${totalIn} / ${totalOut}` : ""}</td>
                  <td className="n">{num(trace.total_cost_usd)?.toFixed(4) ?? ""}</td>
                  <td />
                </tr>
              </tfoot>
            </table>
          </details>
        ) : null}

        <details>
          <summary>Tools run ({evidence?.results?.length ?? 0})</summary>
          {(evidence?.results ?? []).map((tool) => (
            <details key={tool.tool} className="tool">
              <summary>
                <code>{tool.tool}</code> <span className={`status status-${tool.status}`}>{tool.status}</span>{" "}
                <span className="muted small">
                  {tool.facts?.length ?? 0} facts, {tool.gaps?.length ?? 0} gaps
                </span>
              </summary>
              <ul className="small">
                {(tool.facts ?? []).map((fact, i) => (
                  <li key={`f${i}`}>
                    {fact.text}{" "}
                    <button type="button" className="chip" onClick={() => setSelected(fact.id)}>
                      {fact.id}
                    </button>
                  </li>
                ))}
                {(tool.gaps ?? []).map((gap, i) => (
                  <li key={`g${i}`}>
                    <span className="kind kind-gap">gap</span> {gap.text}
                  </li>
                ))}
              </ul>
            </details>
          ))}
        </details>
      </section>

      {found ? (
        <aside className="panel">
          <div className="panel-head">
            <code>{found.id}</code>
            <button type="button" onClick={() => setSelected(null)}>
              Close
            </button>
          </div>
          {found.facts.map((entry, i) => (
            <FactCard key={`f${i}`} fact={entry.fact} tool={entry.tool} />
          ))}
          {found.gaps.map((gap, i) => (
            <GapCard key={`g${i}`} gap={gap} />
          ))}
          {found.derivedFacts.length + found.derivedGaps.length > 0 ? (
            <>
              <h4>
                {found.facts.length + found.gaps.length > 0
                  ? "Also computed from this row"
                  : "This is a source row. Facts computed from it"}
              </h4>
              {found.derivedFacts.map((entry, i) => (
                <FactCard key={`df${i}`} fact={entry.fact} tool={entry.tool} />
              ))}
              {found.derivedGaps.map((gap, i) => (
                <GapCard key={`dg${i}`} gap={gap} />
              ))}
            </>
          ) : null}
          {found.facts.length + found.gaps.length + found.derivedFacts.length + found.derivedGaps.length ===
          0 ? (
            <p className="error">
              This citation does not exist in the evidence file. Treat the line that carries it as
              unsupported.
            </p>
          ) : null}
        </aside>
      ) : null}
    </div>
  );
}
