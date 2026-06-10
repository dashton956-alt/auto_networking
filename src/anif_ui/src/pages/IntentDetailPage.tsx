import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError } from "@/api/client";
import { getAuditRecords, getAuditWhy, getIntent } from "@/api/intents";
import type { AuditRecord, ValidatedIntent } from "@/api/types";
import { Alert, Badge, Card, CardBody, CardHeader, SkeletonText, statusVariant } from "@/components";
import { PipelineStatusTracker } from "@/components/PipelineStatusTracker";
import { stagesFromAuditRecords } from "@/lib/pipelineStages";

export default function IntentDetailPage() {
  const { intentId } = useParams<{ intentId: string }>();
  const [intent, setIntent] = useState<ValidatedIntent | null>(null);
  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [why, setWhy] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!intentId) return;
    let cancelled = false;

    async function load(id: string) {
      setLoading(true);
      setError(null);
      setNotFound(false);
      try {
        const [intentData, auditData, whyData] = await Promise.all([
          getIntent(id),
          getAuditRecords(id),
          getAuditWhy(id),
        ]);
        if (cancelled) return;
        setIntent(intentData);
        setRecords(auditData);
        setWhy(whyData);
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 404) {
          setNotFound(true);
        } else {
          setError(err instanceof Error ? err.message : "Failed to load intent");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load(intentId);
    return () => {
      cancelled = true;
    };
  }, [intentId]);

  if (loading) {
    return (
      <div className="max-w-3xl space-y-4" aria-busy="true">
        <SkeletonText lines={6} />
      </div>
    );
  }

  if (notFound) {
    return (
      <div className="max-w-3xl space-y-4">
        <Alert variant="warning" title="Intent not found">
          No intent exists with ID <span className="font-mono">{intentId}</span>.{" "}
          <Link className="font-medium underline" to="/">
            Back to intent list
          </Link>
        </Alert>
      </div>
    );
  }

  if (error || !intent) {
    return (
      <div className="max-w-3xl space-y-4">
        <Alert variant="danger" title="Could not load intent">
          {error ?? "Unknown error"} —{" "}
          <Link className="font-medium underline" to="/">
            back to intent list
          </Link>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-4">
      <Link to="/" className="text-sm font-medium text-brand-700 hover:underline">
        ← Back to intent list
      </Link>

      <Card aria-label="Intent summary">
        <CardHeader
          title={intent.service}
          subtitle={`Intent ${intent.intent_id}`}
          action={<Badge variant={statusVariant(intent.status)}>{intent.status}</Badge>}
        />
        <CardBody>
          <dl className="grid grid-cols-1 gap-x-6 gap-y-3 text-sm sm:grid-cols-3">
            <div>
              <dt className="font-medium text-chrome-500">Change number</dt>
              <dd className="font-mono text-chrome-900">{intent.change_number}</dd>
            </div>
            <div>
              <dt className="font-medium text-chrome-500">Environment</dt>
              <dd className="text-chrome-900">
                {String(intent.resolved_intent.environment ?? "—")}
              </dd>
            </div>
            <div>
              <dt className="font-medium text-chrome-500">Created</dt>
              <dd>
                <time dateTime={intent.created_at} className="text-chrome-900">
                  {new Date(intent.created_at).toLocaleString()}
                </time>
              </dd>
            </div>
            {intent.git_ref && (
              <div className="sm:col-span-3">
                <dt className="font-medium text-chrome-500">Git provenance</dt>
                <dd className="font-mono text-xs text-chrome-700">
                  {intent.git_ref.repo_url} · {intent.git_ref.path} @{" "}
                  {intent.git_ref.commit_sha.slice(0, 12)}
                </dd>
              </div>
            )}
          </dl>
        </CardBody>
      </Card>

      {intent.warnings.length > 0 && (
        <Alert variant="warning" title="Validation warnings">
          <ul className="list-disc pl-4">
            {intent.warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </Alert>
      )}

      <Card aria-label="Pipeline progress">
        <CardHeader
          title="Pipeline progress"
          subtitle={
            records.length > 0
              ? `Derived from ${records.length} audit record${records.length === 1 ? "" : "s"}`
              : "No audit records yet"
          }
        />
        <CardBody>
          <PipelineStatusTracker states={stagesFromAuditRecords(records)} />
        </CardBody>
      </Card>

      {why && (
        <Card aria-label="Decision explanation">
          <CardHeader title="Why" subtitle="Synthesised from the audit reasoning chain" />
          <CardBody>
            <pre className="whitespace-pre-wrap font-sans text-sm text-chrome-700">{why}</pre>
          </CardBody>
        </Card>
      )}

      <Card aria-label="Resolved intent document">
        <CardHeader title="Resolved intent" subtitle="Defaults applied at validation time" />
        <CardBody>
          <details>
            <summary className="cursor-pointer text-sm font-medium text-brand-700">
              Show resolved intent JSON
            </summary>
            <pre className="mt-3 overflow-x-auto rounded-md bg-chrome-50 p-4 font-mono text-xs text-chrome-800">
              {JSON.stringify(intent.resolved_intent, null, 2)}
            </pre>
          </details>
        </CardBody>
      </Card>
    </div>
  );
}
