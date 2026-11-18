import type { Evidence, Fact, Gap } from "./types";

export const KIND_LABEL: Record<string, string> = {
  data: "measured data",
  calc: "computed",
  reported: "reported by a person",
  gap: "gap",
};

export interface Lookup {
  id: string;
  /** Facts whose own ID is the cited one. Several facts can share a source-row ID. */
  facts: { fact: Fact; tool: string }[];
  gaps: Gap[];
  /** Facts and gaps that list the cited ID among their source rows. */
  derivedFacts: { fact: Fact; tool: string }[];
  derivedGaps: Gap[];
}

export function lookupCitation(evidence: Evidence | undefined, id: string): Lookup {
  const out: Lookup = { id, facts: [], gaps: [], derivedFacts: [], derivedGaps: [] };
  for (const result of evidence?.results ?? []) {
    for (const fact of result.facts ?? []) {
      if (fact.id === id) out.facts.push({ fact, tool: result.tool });
      else if ((fact.rows ?? []).includes(id)) out.derivedFacts.push({ fact, tool: result.tool });
    }
  }
  for (const gap of evidence?.gaps ?? []) {
    if (gap.id === id) out.gaps.push(gap);
    else if ((gap.rows ?? []).includes(id)) out.derivedGaps.push(gap);
  }
  return out;
}

const CITE_ID = "[a-z_]+:[\\w#.\\-]+";
// Same rule as verify.py: IDs, optionally with plain marker words ("reported") in the bracket.
const CITE_PART = `(?:${CITE_ID}|[A-Za-z][A-Za-z' \\-]*)`;
const CITE_RE = new RegExp(`\\[(${CITE_PART}(?:\\s*[,;]\\s*${CITE_PART})*)\\]`, "g");
const CITE_ID_ONLY = new RegExp(`^${CITE_ID}$`);
const FLAG_RE = /(?:\*\*)?\[UNVERIFIED:\s*([^\[\]]*)\](?:\*\*)?/g;

export const CITE_HREF = "#cite=";
export const FLAG_HREF = "#unverified";

/**
 * Rewrites citations and flags into Markdown links with private hrefs, so the Markdown
 * renderer hands them to our link component and everything else renders untouched.
 */
export function markCitations(markdown: string): string {
  return markdown
    .replace(FLAG_RE, (_m, reason: string) => {
      const text = reason.trim().replace(/([\\[\]*_`<>])/g, "\\$1") || "unverified";
      return `[${text}](${FLAG_HREF})`;
    })
    .replace(CITE_RE, (match, inner: string) => {
      const parts = inner.split(/\s*[,;]\s*/);
      const ids = parts.filter((part) => CITE_ID_ONLY.test(part));
      if (ids.length === 0) return match;
      const words = parts.filter((part) => !CITE_ID_ONLY.test(part));
      const chips = ids
        .map((id) => `[${id.replace(/_/g, "\\_")}](${CITE_HREF}${encodeURIComponent(id)})`)
        .join(" ");
      return words.length > 0 ? `${chips} (${words.join(", ")})` : chips;
    });
}
