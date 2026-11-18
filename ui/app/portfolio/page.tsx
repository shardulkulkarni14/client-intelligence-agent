"use client";

import Link from "next/link";
import { Fragment, useEffect, useMemo, useState } from "react";
import { errorMessage } from "@/lib/errors";
import type { PortfolioResponse, Reason, Score } from "@/lib/types";

// Same form as in the briefings ("EUR 752,000"), so a figure reads the same everywhere.
const eurNumber = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 });
const eur = { format: (value: number) => `EUR ${eurNumber.format(value)}` };

/** The tool prints "Y" / "N" (or nothing when no contract is in force); accept a boolean too. */
function yesNo(value: boolean | string | null | undefined): string {
  if (value === null || value === undefined || value === "") return "";
  if (value === true || value === "Y") return "yes";
  if (value === false || value === "N") return "no";
  return String(value);
}

function cites(reason: Reason): string[] {
  if (!reason.cite) return [];
  return Array.isArray(reason.cite) ? reason.cite : [reason.cite];
}

function Reasons({ title, score }: { title: string; score: Score | undefined }) {
  const reasons = score?.reasons ?? [];
  return (
    <div>
      <h4>
        {title}: {score?.score ?? "n/a"}
      </h4>
      {reasons.length === 0 ? (
        <p className="muted small">No reasons recorded.</p>
      ) : (
        <ul className="small">
          {reasons.map((reason, i) => (
            <li key={i}>
              {reason.text}{" "}
              {cites(reason).map((cite) => (
                <code key={cite} className="row">
                  {cite}
                </code>
              ))}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function PortfolioPage() {
  const [data, setData] = useState<PortfolioResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [byGrowth, setByGrowth] = useState(false);
  const [open, setOpen] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetch("/api/portfolio")
      .then(async (res) => {
        const body = await res.json();
        if (!res.ok) throw new Error(errorMessage(body, res.status));
        setData(body as PortfolioResponse);
      })
      .catch((e: Error) => setError(`Could not load the portfolio. ${e.message}`));
  }, []);

  const rows = useMemo(() => {
    const clients = [...(data?.clients ?? [])];
    // The service already ranks by renewal risk; only the growth view needs a re-sort.
    if (byGrowth) clients.sort((a, b) => (b.growth?.score ?? 0) - (a.growth?.score ?? 0));
    return clients;
  }, [data, byGrowth]);

  function toggle(id: string) {
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  if (error) return <p className="error" role="alert">{error}</p>;
  if (!data) return <p className="muted">Loading the portfolio…</p>;

  return (
    <>
      <div className="controls">
        <p className="muted small">
          {rows.length} clients, data as of {data.as_of}. Ranked by {byGrowth ? "growth score" : "renewal risk"}.
        </p>
        <label className="check">
          <input type="checkbox" checked={byGrowth} onChange={(e) => setByGrowth(e.target.checked)} />
          Sort by growth
        </label>
      </div>
      <table className="portfolio">
        <thead>
          <tr>
            <th />
            <th>Client</th>
            <th>Segment, tier</th>
            <th className="n">Annual value</th>
            <th>Contract end</th>
            <th className="n">Days to end</th>
            <th>Auto-renew</th>
            <th className="n">Risk</th>
            <th className="n">Growth</th>
            <th>Data confidence</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <Fragment key={c.client_id}>
              <tr>
                <td>
                  <button type="button" onClick={() => toggle(c.client_id)} aria-expanded={open.has(c.client_id)}>
                    {open.has(c.client_id) ? "Hide" : "Why"}
                  </button>
                </td>
                <td>
                  {c.client_name} <span className="muted small">{c.client_id}</span>
                  <div className="muted small">{c.account_owner}</div>
                </td>
                <td>
                  {c.segment}, {c.tier}
                </td>
                <td className="n">{typeof c.arr_eur === "number" ? eur.format(c.arr_eur) : "none in force"}</td>
                <td>
                  {c.contract_end ?? "none in force"}{" "}
                  {c.contract_id ? <span className="muted small" style={{ whiteSpace: "nowrap" }}>{c.contract_id}</span> : null}
                </td>
                <td className="n">{c.days_to_end ?? ""}</td>
                <td>{yesNo(c.auto_renew)}</td>
                <td className="n">
                  <strong>{c.renewal_risk?.score ?? ""}</strong>
                </td>
                <td className="n">{c.growth?.score ?? ""}</td>
                <td>{c.confidence ?? ""}</td>
                <td>
                  <Link href={`/?client=${encodeURIComponent(c.client_id)}`}>Briefing</Link>
                </td>
              </tr>
              {open.has(c.client_id) ? (
                <tr className="expanded">
                  <td />
                  <td colSpan={10}>
                    <div className="reasons">
                      <Reasons title="Renewal risk" score={c.renewal_risk} />
                      <Reasons title="Growth" score={c.growth} />
                    </div>
                  </td>
                </tr>
              ) : null}
            </Fragment>
          ))}
        </tbody>
      </table>
    </>
  );
}
