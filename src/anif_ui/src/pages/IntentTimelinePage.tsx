import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { verifyChain, type ChainVerification } from "@/api/audit";
import { getAuditRecords, getAuditWhy } from "@/api/intents";
import type { AuditRecord } from "@/api/types";
import { Alert, Badge, Card, CardBody, CardHeader, SkeletonText, statusVariant } from "@/components";
import { AuditRecordDetail } from "@/components/AuditRecordDetail";

const outcomeVariant = (outcome: string) =>
  outcome === "failure" ? "failed" : statusVariant(outcome);

export default function IntentTimelinePage() {
  const { intentId } = useParams<{ intentId: string }>();
  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [why, setWhy] = useState("");
  const [verification, setVerification] = useState<ChainVerification | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  const load = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const [auditData, whyData, verifyData] = await Promise.all([
        getAuditRecords(id),
        getAuditWhy(id).catch(() => ""),
        verifyChain(id).catch(() => null),
      ]);
      setRecords(auditData);
      setWhy(whyData);
      setVerification(verifyData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load audit trail");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (intentId) void load(intentId);
  }, [intentId, load]);

  if (loading) {
    return (
      <div className="max-w-4xl space-y-4" aria-busy="true">
        <SkeletonText lines={8} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl space-y-4">
        <Alert variant="danger" title="Could not load audit trail">
          {error} —{" "}
          <Link className="font-medium underline" to="/audit">
            back to audit trail
          </Link>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-4xl space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <Link to="/audit" className="text-sm font-medium text-brand-700 hover:underline">
          ← Back to audit trail
        </Link>
        <Link
          to={`/intents/${intentId}`}
          className="text-sm font-medium text-brand-700 hover:underline"
        >
          View intent details →
        </Link>
      </div>

      {/* Hash-chain verification (ANIF-107 §4.7.3) */}
      {verification &&
        (verification.valid ? (
          <Alert variant="success" title="Hash chain verified">
            All {verification.record_count} record
            {verification.record_count === 1 ? "" : "s"} in this chain verified — the trail
            has not been tampered with.
          </Alert>
        ) : (
          <Alert variant="danger" title="Hash chain broken">
            Chain verification failed at record{" "}
            <span className="font-mono">{verification.broken_at ?? "unknown"}</span>. Treat
            this audit trail as untrusted and escalate.
          </Alert>
        ))}

      {why && (
        <Card aria-label="Decision explanation">
          <CardHeader title="Why" subtitle="Synthesised from the audit reasoning chain" />
          <CardBody>
            <pre className="whitespace-pre-wrap font-sans text-sm text-chrome-700">{why}</pre>
          </CardBody>
        </Card>
      )}

      <Card aria-label="Intent history timeline">
        <CardHeader
          title="History timeline"
          subtitle={`Intent ${intentId} — ${records.length} record${records.length === 1 ? "" : "s"}, oldest first`}
        />
        <CardBody>
          {records.length === 0 ? (
            <p className="text-sm text-chrome-600">
              No audit records exist for this intent ID.
            </p>
          ) : (
            <ol aria-label="Audit events, oldest first" className="space-y-0">
              {records.map((record, index) => {
                const isOpen = expanded === record.record_id;
                const isLast = index === records.length - 1;
                return (
                  <li key={record.record_id} className="relative flex gap-4 pb-1">
                    {/* Timeline rail */}
                    <div className="flex flex-col items-center">
                      <span
                        aria-hidden="true"
                        className="mt-1.5 flex h-3 w-3 shrink-0 rounded-full border-2 border-brand-600 bg-white"
                      />
                      {!isLast && (
                        <span aria-hidden="true" className="w-px flex-1 bg-chrome-200" />
                      )}
                    </div>

                    <div className="min-w-0 flex-1 pb-4">
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge>{record.stage}</Badge>
                        <Badge variant={outcomeVariant(record.outcome)}>{record.outcome}</Badge>
                        <time
                          dateTime={record.timestamp}
                          className="text-xs text-chrome-600"
                        >
                          {new Date(record.timestamp).toLocaleString()}
                        </time>
                        <span className="text-xs text-chrome-600">
                          {record.duration_ms} ms
                        </span>
                        {record.operator_id && (
                          <span className="text-xs text-chrome-600">
                            by {record.operator_id}
                          </span>
                        )}
                        <button
                          type="button"
                          aria-expanded={isOpen}
                          aria-controls={`timeline-detail-${record.record_id}`}
                          onClick={() => setExpanded(isOpen ? null : record.record_id)}
                          className="ml-auto rounded px-2 py-1 text-xs font-medium text-brand-700 hover:bg-brand-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500"
                        >
                          {isOpen ? "Hide reasoning" : "Show reasoning"}
                        </button>
                      </div>
                      {isOpen && (
                        <div
                          id={`timeline-detail-${record.record_id}`}
                          className="mt-3 rounded-md border border-chrome-200 bg-chrome-50 p-4"
                        >
                          <AuditRecordDetail record={record} />
                        </div>
                      )}
                    </div>
                  </li>
                );
              })}
            </ol>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
