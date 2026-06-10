/** Derives per-stage pipeline states for the PipelineStatusTracker. */

import type { AuditRecord, OrchestrateResponse, PipelineStage, StageState } from "@/api/types";
import { PIPELINE_STAGES } from "@/api/types";

export type StageStates = Record<PipelineStage, StageState>;

function allNotReached(): StageStates {
  return Object.fromEntries(PIPELINE_STAGES.map((s) => [s, "not_reached"])) as StageStates;
}

/** Derive per-stage states from a POST /orchestrate response. */
export function stagesFromOrchestrate(result: OrchestrateResponse): StageStates {
  const states = allNotReached();

  for (const stage of PIPELINE_STAGES) {
    if (result.stages && result.stages[stage] !== undefined) {
      states[stage] = "pass";
    }
  }

  if (result.status === "pipeline_complete") {
    const exec = result.stages?.execute as { status?: string } | undefined;
    states.execute = exec?.status === "dry_run" ? "dry_run" : "pass";
    return states;
  }

  const failedStage = result.stage as PipelineStage | undefined;
  if (failedStage && PIPELINE_STAGES.includes(failedStage)) {
    if (result.status === "failed" || result.status === "precondition_failed") {
      states[failedStage] = "failed";
    } else if (result.status === "blocked") {
      states[failedStage] = "blocked";
    } else if (result.status === "pending_approval") {
      states[failedStage] = "pending_approval";
    }
  }
  return states;
}

/** Derive per-stage states from GET /audit/{intent_id} records. */
export function stagesFromAuditRecords(records: AuditRecord[]): StageStates {
  const states = allNotReached();

  const outcomeToState: Record<string, StageState> = {
    success: "pass",
    failure: "failed",
    blocked: "blocked",
    escalated: "pending_approval",
  };

  for (const record of records) {
    const stage = record.stage as PipelineStage;
    if (!PIPELINE_STAGES.includes(stage)) continue;
    states[stage] = outcomeToState[record.outcome] ?? "pass";
  }
  return states;
}
