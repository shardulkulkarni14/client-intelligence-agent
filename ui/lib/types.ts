// Shapes of the JSON the Python service returns. The UI only reads them.

export interface HealthResponse {
  status: string;
  as_of: string;
  model: string;
  model_key_present: boolean;
}

export interface ClientRef {
  client_id: string;
  client_name: string;
  segment: string;
  tier: string;
  account_owner: string;
}

export interface TriggerRef {
  name: string;
  question: string;
  sections: string[];
}

export interface ListResponse {
  as_of: string;
  clients: ClientRef[];
  triggers: TriggerRef[];
}

export interface Fact {
  id: string;
  text: string;
  rows: string[];
  kind: string;
  topic?: string;
  signal?: string;
}

export interface Gap {
  id?: string;
  code: string;
  text: string;
  rows: string[];
}

export interface ToolResult {
  tool: string;
  status: string;
  facts: Fact[];
  gaps: Gap[];
  data?: unknown;
}

export interface Violation {
  line: number | string;
  kind: string;
  token: string;
  detail: string;
}

export interface VerificationPass {
  ok: boolean;
  numbers_checked: number;
  citations_checked: number;
  violations: Violation[];
  uncited_lines: number;
}

export interface TraceStep {
  name: string;
  kind: string;
  seconds?: number;
  detail?: unknown;
  [key: string]: unknown;
}

export interface Trace {
  model?: string;
  total_seconds?: number;
  total_cost_usd?: number;
  steps?: TraceStep[];
}

export interface Evidence {
  request?: Record<string, unknown>;
  plan?: { trigger: string; question: string; tools: string[]; sections: string[] };
  results?: ToolResult[];
  gaps?: Gap[];
  writer?: { mode?: string; repaired?: boolean };
  verification?: { first_pass?: VerificationPass; final?: VerificationPass };
  trace?: Trace;
}

export interface BriefingResponse {
  ok: boolean;
  error: string | null;
  client_id?: string;
  client_name?: string;
  trigger?: string;
  briefing?: string;
  evidence?: Evidence;
  flagged?: number;
  repaired?: boolean;
}

export interface Reason {
  text: string;
  cite?: string | string[] | null;
}

export interface Score {
  score: number;
  reasons: Reason[];
}

export interface PortfolioClient extends ClientRef {
  arr_eur: number | null;
  contract_id: string | null;
  contract_end: string | null;
  days_to_end: number | null;
  auto_renew: boolean | string | null;
  confidence: string | null;
  renewal_risk: Score;
  growth: Score;
}

export interface PortfolioResponse {
  as_of: string;
  clients: PortfolioClient[];
}
