/** Types mirroring the ANIF platform REST API schemas (ANIF-300/301/107). */

export interface GitIntentRef {
  repo_url: string;
  path: string;
  commit_sha: string;
}

export interface ValidatedIntent {
  intent_id: string;
  change_number: number;
  version: string;
  service: string;
  status: string;
  git_ref: GitIntentRef | null;
  resolved_intent: Record<string, unknown>;
  warnings: string[];
  created_at: string;
}

export interface IntentListResponse {
  items: ValidatedIntent[];
  total: number;
  limit: number;
  offset: number;
}

export interface ValidationResult {
  intent_id: string | null;
  status: string; // "validated" | "validation_failed"
  errors: string[];
  warnings: string[];
  validated_intent: Record<string, unknown> | null;
}

/** Draft intent document submitted to validate-intent / orchestrate. */
export interface IntentDraft {
  service: string;
  environment?: string;
  priority?: string;
  objectives: {
    latency_ms?: number;
    availability_percent?: number;
    throughput_mbps?: number;
  };
  constraints: {
    region?: string;
    encryption?: boolean;
    allowed_zones?: string[];
  };
  policies?: string[];
}

export const PIPELINE_STAGES = [
  "validate",
  "policy",
  "risk",
  "decision",
  "governance",
  "execute",
] as const;

export type PipelineStage = (typeof PIPELINE_STAGES)[number];

export type StageState =
  | "pass"
  | "failed"
  | "blocked"
  | "pending_approval"
  | "dry_run"
  | "not_reached";

/**
 * POST /orchestrate response. Terminal statuses:
 * pipeline_complete | failed | blocked | pending_approval | precondition_failed
 */
export interface OrchestrateResponse {
  status: string;
  intent_id?: string;
  stage?: string;
  stages?: Partial<Record<PipelineStage, Record<string, unknown>>>;
  dry_run?: boolean;
  errors?: string[];
  warnings?: string[];
  error?: string;
  ticket_id?: string;
  ticket_expires_at?: string;
  policy_result?: Record<string, unknown>;
  risk_result?: Record<string, unknown>;
  governance_result?: Record<string, unknown>;
}

/** One audit record as returned by GET /audit/{intent_id} (ANIF-107). */
export interface AuditRecord {
  record_id: string;
  intent_id: string;
  stage: PipelineStage | string;
  timestamp: string;
  outcome: "success" | "failure" | "blocked" | "escalated" | string;
  duration_ms: number;
  operator_id?: string | null;
  input_summary: Record<string, unknown>;
  output_summary: Record<string, unknown>;
  reasoning_chain?: Array<{
    step: number;
    description: string;
    decision: string;
    rationale?: string;
  }>;
  policies_evaluated?: string[];
  policies_violated?: string[];
}
