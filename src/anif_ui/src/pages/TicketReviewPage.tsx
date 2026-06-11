import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  approveTicket,
  listTickets,
  rejectTicket,
  type Operator,
  type TicketSummary,
} from "@/api/governance";
import { getAuditRecords, getAuditWhy, getIntent } from "@/api/intents";
import type { AuditRecord, ValidatedIntent } from "@/api/types";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  CountdownTimer,
  Input,
  RiskMeter,
  SkeletonText,
} from "@/components";
import { OperatorBar } from "@/components/OperatorBar";
import { PipelineStatusTracker } from "@/components/PipelineStatusTracker";
import { stagesFromAuditRecords } from "@/lib/pipelineStages";

type ConfirmAction = "approve" | "reject" | null;

interface ActionOutcome {
  kind: "approved" | "rejected";
  by: string;
  at: string;
}

function findStage(records: AuditRecord[], stage: string): AuditRecord | undefined {
  return records.find((r) => r.stage === stage);
}

function reasoningText(record: AuditRecord | undefined): string | null {
  const steps = record?.reasoning_chain ?? [];
  if (steps.length === 0) return null;
  return steps
    .map((s) => `${s.description} → ${s.decision}${s.rationale ? ` (${s.rationale})` : ""}`)
    .join("\n");
}

export default function TicketReviewPage() {
  const { ticketId } = useParams<{ ticketId: string }>();
  const [ticket, setTicket] = useState<TicketSummary | null>(null);
  const [intent, setIntent] = useState<ValidatedIntent | null>(null);
  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [why, setWhy] = useState("");
  const [loading, setLoading] = useState(true);
  const [notPending, setNotPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [operator, setOperator] = useState<Operator>({
    operatorId: "operator-1",
    role: "senior_engineer",
  });
  const [confirm, setConfirm] = useState<ConfirmAction>(null);
  const [notes, setNotes] = useState("");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [outcome, setOutcome] = useState<ActionOutcome | null>(null);

  const load = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    setNotPending(false);
    try {
      const list = await listTickets();
      const found = list.tickets.find((t) => t.ticket_id === id) ?? null;
      if (!found) {
        setNotPending(true);
        return;
      }
      setTicket(found);
      // Evidence calls degrade individually: a ticket can exist without a
      // registered intent (e.g. created via /governance/check), and the
      // review page must still render for the approve/reject decision.
      const [intentData, auditData, whyData] = await Promise.all([
        getIntent(found.intent_id).catch(() => null),
        getAuditRecords(found.intent_id).catch(() => []),
        getAuditWhy(found.intent_id).catch(() => ""),
      ]);
      setIntent(intentData);
      setRecords(auditData);
      setWhy(whyData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load ticket");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (ticketId) void load(ticketId);
  }, [ticketId, load]);

  async function runAction(action: "approve" | "reject") {
    if (!ticket) return;
    setBusy(true);
    setActionError(null);
    try {
      if (action === "approve") {
        const response = await approveTicket(ticket.ticket_id, operator, notes.trim() || null);
        setOutcome({ kind: "approved", by: response.approved_by, at: response.approved_at });
      } else {
        const response = await rejectTicket(ticket.ticket_id, operator, reason.trim());
        setOutcome({ kind: "rejected", by: response.rejected_by, at: response.rejected_at });
      }
      setConfirm(null);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <div className="max-w-4xl space-y-4" aria-busy="true">
        <SkeletonText lines={8} />
      </div>
    );
  }

  if (notPending) {
    return (
      <div className="max-w-4xl space-y-4">
        <Alert variant="warning" title="Ticket not pending">
          Ticket <span className="font-mono">{ticketId}</span> is not in the pending queue —
          it may have been approved, rejected, or expired.{" "}
          <Link className="font-medium underline" to="/approvals">
            Back to approval queue
          </Link>
        </Alert>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div className="max-w-4xl space-y-4">
        <Alert variant="danger" title="Could not load ticket">
          {error ?? "Unknown error"} —{" "}
          <Link className="font-medium underline" to="/approvals">
            back to approval queue
          </Link>
        </Alert>
      </div>
    );
  }

  const riskRecord = findStage(records, "risk");
  const governanceRecord = findStage(records, "governance");
  const policyRecord = findStage(records, "policy");
  const decisionRecord = findStage(records, "decision");

  const riskJustification =
    reasoningText(riskRecord) ??
    (riskRecord
      ? `Risk ${String(riskRecord.output_summary.risk_score ?? "?")} / trust ${String(
          riskRecord.output_summary.trust_score ?? "?",
        )} — safety decision: ${String(riskRecord.output_summary.safety_decision ?? "unknown")}`
      : null);

  const governanceRule = governanceRecord
    ? String(governanceRecord.output_summary.triggered_rule ?? "none")
    : null;
  const governanceRationale = reasoningText(governanceRecord);

  const recommendedAction = decisionRecord
    ? String(decisionRecord.output_summary.recommended_action ?? "")
    : "";
  const rollbackPlan = recommendedAction
    ? `Reverse ${recommendedAction} within 60 seconds of failure detection (target: pipeline-auto).`
    : null;

  const actionsDisabled = busy || outcome !== null;

  return (
    <div className="max-w-4xl space-y-4">
      <Link to="/approvals" className="text-sm font-medium text-brand-700 hover:underline">
        ← Back to approval queue
      </Link>

      {/* Ticket summary — decision_summary, risk, submitter, expiry (§4.7) */}
      <Card aria-label="Ticket summary">
        <CardHeader
          title={ticket.decision_summary}
          subtitle={`Ticket ${ticket.ticket_id}`}
          action={<Badge variant="escalated">pending review</Badge>}
        />
        <CardBody>
          <dl className="grid grid-cols-1 gap-x-6 gap-y-3 text-sm sm:grid-cols-3">
            <div>
              <dt className="font-medium text-chrome-500">Requested by</dt>
              <dd className="text-chrome-900">{ticket.requested_by}</dd>
            </div>
            <div>
              <dt className="font-medium text-chrome-500">Created</dt>
              <dd>
                <time dateTime={ticket.created_at} className="text-chrome-900">
                  {new Date(ticket.created_at).toLocaleString()}
                </time>
              </dd>
            </div>
            <div>
              <dt className="font-medium text-chrome-500">Expires in</dt>
              <dd>
                <CountdownTimer expiresAt={ticket.expires_at} />
              </dd>
            </div>
            <div className="sm:col-span-3">
              <dt className="font-medium text-chrome-500">Risk score</dt>
              <dd className="mt-1 max-w-sm">
                <RiskMeter score={ticket.risk_score} />
              </dd>
            </div>
            <div className="sm:col-span-3">
              <dt className="font-medium text-chrome-500">Intent</dt>
              <dd>
                <Link
                  to={`/intents/${ticket.intent_id}`}
                  className="font-mono text-xs text-brand-700 hover:underline"
                >
                  {ticket.intent_id}
                </Link>
              </dd>
            </div>
          </dl>
        </CardBody>
      </Card>

      {/* Pipeline progress + per-stage evidence (§4.7) */}
      <Card aria-label="Review evidence">
        <CardHeader title="Review evidence" subtitle="Derived from the audit trail" />
        <CardBody className="space-y-5">
          <PipelineStatusTracker states={stagesFromAuditRecords(records)} />

          <section aria-label="Risk score justification">
            <h3 className="text-sm font-semibold text-chrome-900">Risk score justification</h3>
            <p className="mt-1 whitespace-pre-wrap text-sm text-chrome-700">
              {riskJustification ?? "No risk-stage audit record found."}
            </p>
          </section>

          <section aria-label="Governance rule triggered">
            <h3 className="text-sm font-semibold text-chrome-900">Governance rule triggered</h3>
            <p className="mt-1 text-sm text-chrome-700">
              {governanceRule ? (
                <Badge variant="escalated">{governanceRule}</Badge>
              ) : (
                "No governance-stage audit record found."
              )}
            </p>
            {governanceRationale && (
              <p className="mt-1 whitespace-pre-wrap text-sm text-chrome-700">
                {governanceRationale}
              </p>
            )}
          </section>

          <section aria-label="Policy evaluation results">
            <h3 className="text-sm font-semibold text-chrome-900">Policy evaluation results</h3>
            {policyRecord ? (
              <ul className="mt-1 space-y-1 text-sm text-chrome-700">
                {(policyRecord.policies_evaluated ?? []).map((p) => {
                  const violated = (policyRecord.policies_violated ?? []).includes(p);
                  return (
                    <li key={p} className="flex items-center gap-2">
                      <Badge variant={violated ? "danger" : "success"}>
                        {violated ? "deny" : "pass"}
                      </Badge>
                      {p}
                    </li>
                  );
                })}
                {(policyRecord.policies_evaluated ?? []).length === 0 && (
                  <li>No policies were applicable to this intent.</li>
                )}
              </ul>
            ) : (
              <p className="mt-1 text-sm text-chrome-700">No policy-stage audit record found.</p>
            )}
          </section>

          <section aria-label="Rollback plan">
            <h3 className="text-sm font-semibold text-chrome-900">Rollback plan</h3>
            <p className="mt-1 text-sm text-chrome-700">
              {rollbackPlan ?? "Rollback plan not yet generated (produced at execution time)."}
            </p>
          </section>

          <section aria-label="Full reasoning chain">
            <h3 className="text-sm font-semibold text-chrome-900">Full reasoning chain</h3>
            <pre className="mt-1 whitespace-pre-wrap font-sans text-sm text-chrome-700">
              {why || "No reasoning recorded yet."}
            </pre>
          </section>
        </CardBody>
      </Card>

      {/* Proposed action details (§4.7) */}
      <Card aria-label="Proposed action details">
        <CardHeader title="Proposed action details" subtitle="Resolved intent payload" />
        <CardBody>
          {intent ? (
            <details open>
              <summary className="cursor-pointer text-sm font-medium text-brand-700">
                Resolved intent JSON
              </summary>
              <pre className="mt-3 overflow-x-auto rounded-md bg-chrome-50 p-4 font-mono text-xs text-chrome-800">
                {JSON.stringify(intent.resolved_intent, null, 2)}
              </pre>
            </details>
          ) : (
            <p className="text-sm text-chrome-700">Intent payload unavailable.</p>
          )}
        </CardBody>
      </Card>

      {/* Decision controls with confirmation step (§4.7) */}
      <Card aria-label="Decision">
        <CardHeader
          title="Decision"
          subtitle="Approve requires senior_engineer; all actions are audited"
        />
        <CardBody className="space-y-4">
          <OperatorBar operator={operator} onChange={setOperator} />

          <div aria-live="polite" className="space-y-4">
            {outcome && (
              <Alert
                variant={outcome.kind === "approved" ? "success" : "info"}
                title={`Ticket ${outcome.kind}`}
              >
                {outcome.kind === "approved" ? "Approved" : "Rejected"} by {outcome.by} at{" "}
                {new Date(outcome.at).toLocaleString()}. An audit record has been written.{" "}
                <Link className="font-medium underline" to="/approvals">
                  Back to approval queue
                </Link>
              </Alert>
            )}

            {actionError && (
              <Alert variant="danger" title="Action refused">
                {actionError}
              </Alert>
            )}
          </div>

          {!outcome && confirm === null && (
            <div className="flex gap-2">
              <Button onClick={() => setConfirm("approve")} disabled={actionsDisabled}>
                Approve…
              </Button>
              <Button
                variant="danger"
                onClick={() => setConfirm("reject")}
                disabled={actionsDisabled}
              >
                Reject…
              </Button>
            </div>
          )}

          {!outcome && confirm === "approve" && (
            <form
              className="space-y-3 rounded-md border border-chrome-200 p-4"
              onSubmit={(e) => {
                e.preventDefault();
                void runAction("approve");
              }}
            >
              <p className="text-sm font-medium text-chrome-900">
                Confirm approval of {ticket.ticket_id}?
              </p>
              <Input
                label="Notes (optional)"
                id="approval-notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
              <div className="flex gap-2">
                <Button type="submit" loading={busy} disabled={busy}>
                  Confirm approval
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setConfirm(null)}
                  disabled={busy}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}

          {!outcome && confirm === "reject" && (
            <form
              className="space-y-3 rounded-md border border-chrome-200 p-4"
              onSubmit={(e) => {
                e.preventDefault();
                if (reason.trim()) void runAction("reject");
              }}
            >
              <p className="text-sm font-medium text-chrome-900">
                Confirm rejection of {ticket.ticket_id}?
              </p>
              <Input
                label="Reason"
                id="rejection-reason"
                required
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                helperText="A reason is required for rejection"
              />
              <div className="flex gap-2">
                <Button
                  type="submit"
                  variant="danger"
                  loading={busy}
                  disabled={busy || !reason.trim()}
                >
                  Confirm rejection
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setConfirm(null)}
                  disabled={busy}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
