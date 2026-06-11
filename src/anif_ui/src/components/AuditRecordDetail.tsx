import type { AuditRecord } from "@/api/types";
import { Badge } from "@/components";

function SummaryBlock({ title, data }: { title: string; data: Record<string, unknown> }) {
  const entries = Object.entries(data ?? {});
  return (
    <div>
      <h4 className="text-xs font-semibold uppercase tracking-wide text-chrome-600">{title}</h4>
      {entries.length > 0 ? (
        <dl className="mt-1 space-y-0.5">
          {entries.map(([key, value]) => (
            <div key={key} className="flex gap-2 text-xs">
              <dt className="font-medium text-chrome-600">{key}:</dt>
              <dd className="break-all font-mono text-chrome-800">
                {value === null ? "null" : String(value)}
              </dd>
            </div>
          ))}
        </dl>
      ) : (
        <p className="mt-1 text-xs text-chrome-600">empty</p>
      )}
    </div>
  );
}

/** Reasoning chain, input/output summaries, and policy results for one audit record. */
export function AuditRecordDetail({ record }: { record: AuditRecord }) {
  const steps = record.reasoning_chain ?? [];
  const evaluated = record.policies_evaluated ?? [];
  const violated = record.policies_violated ?? [];

  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wide text-chrome-600">
          Reasoning chain
        </h4>
        {steps.length > 0 ? (
          <ol className="mt-1 space-y-2">
            {steps.map((step) => (
              <li key={step.step} className="text-sm text-chrome-800">
                <span className="font-semibold">{step.step}.</span> {step.description} →{" "}
                <span className="font-medium">{step.decision}</span>
                {step.rationale && (
                  <p className="mt-0.5 text-xs text-chrome-600">{step.rationale}</p>
                )}
              </li>
            ))}
          </ol>
        ) : (
          <p className="mt-1 text-xs text-chrome-600">
            No reasoning steps recorded for this stage.
          </p>
        )}
      </div>

      {evaluated.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-chrome-600">
            Policies evaluated
          </h4>
          <ul className="mt-1 flex flex-wrap gap-2">
            {evaluated.map((policy) => (
              <li key={policy} className="flex items-center gap-1.5 text-xs text-chrome-800">
                <Badge variant={violated.includes(policy) ? "danger" : "success"}>
                  {violated.includes(policy) ? "deny" : "pass"}
                </Badge>
                {policy}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <SummaryBlock title="Input summary" data={record.input_summary} />
        <SummaryBlock title="Output summary" data={record.output_summary} />
      </div>

      <p className="font-mono text-2xs text-chrome-600">record {record.record_id}</p>
    </div>
  );
}
