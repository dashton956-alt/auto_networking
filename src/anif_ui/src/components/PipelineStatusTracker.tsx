import type { PipelineStage, StageState } from "@/api/types";
import { PIPELINE_STAGES } from "@/api/types";
import type { StageStates } from "@/lib/pipelineStages";

const STAGE_LABELS: Record<PipelineStage, string> = {
  validate: "Validate",
  policy: "Policy",
  risk: "Risk",
  decision: "Decision",
  governance: "Governance",
  execute: "Execute",
};

const STATE_STYLES: Record<StageState, { circle: string; label: string; icon: string }> = {
  pass: { circle: "bg-status-success text-white", label: "text-chrome-700", icon: "✓" },
  failed: { circle: "bg-status-danger text-white", label: "text-status-danger", icon: "✕" },
  blocked: { circle: "bg-orange-600 text-white", label: "text-orange-700", icon: "■" },
  pending_approval: { circle: "bg-violet-600 text-white", label: "text-violet-700", icon: "⏸" },
  dry_run: { circle: "bg-brand-600 text-white", label: "text-brand-700", icon: "◌" },
  not_reached: { circle: "bg-chrome-100 text-chrome-500", label: "text-chrome-500", icon: "" },
};

const STATE_TEXT: Record<StageState, string> = {
  pass: "passed",
  failed: "failed",
  blocked: "blocked",
  pending_approval: "pending approval",
  dry_run: "dry run — not executed",
  not_reached: "not reached",
};

interface PipelineStatusTrackerProps {
  states: StageStates;
  className?: string;
}

/**
 * Six-stage pipeline progress indicator:
 * validate → policy → risk → decision → governance → execute.
 */
export function PipelineStatusTracker({ states, className = "" }: PipelineStatusTrackerProps) {
  // The "current" stage is the first non-pass stage that was reached.
  const current = PIPELINE_STAGES.find(
    (s) => states[s] !== "pass" && states[s] !== "not_reached",
  );

  return (
    <ol
      aria-label="Pipeline progress"
      className={["flex flex-wrap items-start gap-x-2 gap-y-3", className].join(" ")}
    >
      {PIPELINE_STAGES.map((stage, index) => {
        const state = states[stage];
        const style = STATE_STYLES[state];
        return (
          <li
            key={stage}
            aria-current={stage === current ? "step" : undefined}
            className="flex items-center gap-2"
          >
            <span
              aria-hidden="true"
              className={[
                "flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold",
                style.circle,
              ].join(" ")}
            >
              {style.icon || index + 1}
            </span>
            <span className={["text-xs font-medium", style.label].join(" ")}>
              {STAGE_LABELS[stage]}
              <span className="sr-only"> — {STATE_TEXT[state]}</span>
            </span>
            {index < PIPELINE_STAGES.length - 1 && (
              <span aria-hidden="true" className="mx-1 h-px w-6 bg-chrome-200" />
            )}
          </li>
        );
      })}
    </ol>
  );
}
