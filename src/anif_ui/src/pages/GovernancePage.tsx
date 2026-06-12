import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listAuditRecords } from "@/api/audit";
import {
  getCouncilSessions,
  getStrikes,
  type CouncilSession,
  type StrikeRecord,
} from "@/api/dashboard";
import type { AuditRecord } from "@/api/types";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  RiskMeter,
  SkeletonText,
  statusVariant,
  type BadgeVariant,
} from "@/components";

const REFRESH_INTERVAL_MS = 15_000;

const COUNCIL_DECISION_VARIANT: Record<string, BadgeVariant> = {
  approved: "success",
  completed: "success",
  blocked: "blocked",
  conditional: "warning",
  deferred: "pending",
  escalated: "escalated",
  timed_out: "danger",
  pending: "pending",
};

interface DashboardData {
  riskRecords: AuditRecord[];
  governanceRecords: AuditRecord[];
  sessions: CouncilSession[];
  strikes: StrikeRecord[];
  strikesTotal: number;
}

export default function GovernancePage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);

  const load = useCallback(async (background: boolean) => {
    if (!background) setLoading(true);
    try {
      const [riskRecords, governanceRecords, councils, strikes] = await Promise.all([
        listAuditRecords({ stage: "risk", limit: 10 }),
        listAuditRecords({ stage: "governance", limit: 50 }),
        getCouncilSessions(10),
        getStrikes(25),
      ]);
      setData({
        riskRecords,
        governanceRecords,
        sessions: councils.sessions,
        strikes: strikes.strikes,
        strikesTotal: strikes.total,
      });
      setError(null);
      setUpdatedAt(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load(false);
    const id = setInterval(() => void load(true), REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, [load]);

  if (loading) {
    return (
      <div className="space-y-4" aria-busy="true">
        <SkeletonText lines={10} />
      </div>
    );
  }

  if (error && !data) {
    return (
      <Alert variant="danger" title="Could not load dashboard">
        {error} — is the platform API running?
      </Alert>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-chrome-600" aria-live="polite">
          Auto-refreshes every 15 seconds
          {updatedAt && <> — last updated {updatedAt.toLocaleTimeString()}</>}
        </p>
        <Button variant="secondary" size="sm" onClick={() => void load(false)}>
          Refresh
        </Button>
      </div>

      {error && (
        <Alert variant="warning" title="Refresh failed">
          Showing the last loaded data — {error}
        </Alert>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <RiskPanel records={data.riskRecords} />
        <GovernanceActivityPanel records={data.governanceRecords} />
        <CouncilFeed sessions={data.sessions} />
        <StrikesLog strikes={data.strikes} total={data.strikesTotal} />
      </div>
    </div>
  );
}

// ── Live risk score panel ──────────────────────────────────────────────────

function RiskPanel({ records }: { records: AuditRecord[] }) {
  const latest = records[0];
  const latestRisk = latest ? Number(latest.output_summary.risk_score ?? 0) : null;
  const latestTrust = latest ? Number(latest.output_summary.trust_score ?? 0) : null;

  return (
    <Card aria-label="Live risk scores">
      <CardHeader
        title="Live risk scores"
        subtitle="Most recent risk-stage evaluations (ANIF-304)"
      />
      <CardBody className="space-y-4">
        {latest && latestRisk !== null ? (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-chrome-700">
                Latest intent{" "}
                <Link
                  to={`/audit/${latest.intent_id}`}
                  className="font-mono text-xs text-brand-700 hover:underline"
                >
                  {latest.intent_id.slice(0, 8)}…
                </Link>
              </span>
              <span className="text-xs text-chrome-600">trust {latestTrust}</span>
            </div>
            <RiskMeter score={latestRisk} />
          </div>
        ) : (
          <p className="text-sm text-chrome-600">No risk evaluations recorded yet.</p>
        )}

        {records.length > 1 && (
          <ul aria-label="Recent risk evaluations" className="divide-y divide-chrome-100">
            {records.slice(1, 6).map((record) => (
              <li key={record.record_id} className="flex items-center justify-between gap-2 py-2">
                <Link
                  to={`/audit/${record.intent_id}`}
                  className="font-mono text-xs text-brand-700 hover:underline"
                >
                  {record.intent_id.slice(0, 8)}…
                </Link>
                <span className="flex items-center gap-2 text-xs text-chrome-700">
                  risk {String(record.output_summary.risk_score ?? "?")} · trust{" "}
                  {String(record.output_summary.trust_score ?? "?")}
                  <Badge
                    variant={
                      record.output_summary.safety_decision === "block"
                        ? "blocked"
                        : record.output_summary.safety_decision === "warn"
                          ? "warning"
                          : "success"
                    }
                  >
                    {String(record.output_summary.safety_decision ?? "allow")}
                  </Badge>
                </span>
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  );
}

// ── Governance activity (observability) ────────────────────────────────────

function GovernanceActivityPanel({ records }: { records: AuditRecord[] }) {
  const counts = { auto: 0, manual_review: 0, block: 0 };
  for (const record of records) {
    const mode = String(record.output_summary.mode ?? "");
    if (mode in counts) counts[mode as keyof typeof counts] += 1;
  }
  const total = records.length;

  const rows: Array<{ label: string; count: number; bar: string }> = [
    { label: "auto", count: counts.auto, bar: "bg-status-success" },
    { label: "manual_review", count: counts.manual_review, bar: "bg-violet-600" },
    { label: "block", count: counts.block, bar: "bg-status-danger" },
  ];

  return (
    <Card aria-label="Governance activity">
      <CardHeader
        title="Governance activity"
        subtitle={`Mode routing across the last ${total} governance evaluations`}
      />
      <CardBody className="space-y-3">
        {total === 0 ? (
          <p className="text-sm text-chrome-600">No governance evaluations recorded yet.</p>
        ) : (
          rows.map((row) => {
            const percent = total > 0 ? Math.round((row.count / total) * 100) : 0;
            return (
              <div key={row.label}>
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-chrome-700">{row.label}</span>
                  <span className="text-chrome-600">
                    {row.count} ({percent}%)
                  </span>
                </div>
                <div
                  role="meter"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={percent}
                  aria-label={`${row.label}: ${percent} percent`}
                  className="mt-1 h-2 w-full overflow-hidden rounded-full bg-chrome-100"
                >
                  <div className={`h-full ${row.bar}`} style={{ width: `${percent}%` }} />
                </div>
              </div>
            );
          })
        )}
        <p className="text-xs text-chrome-600">
          Prometheus counters are exposed at <span className="font-mono">/metrics</span> for
          the full observability stack (ANIF-401).
        </p>
      </CardBody>
    </Card>
  );
}

// ── Council decision feed ──────────────────────────────────────────────────

function CouncilFeed({ sessions }: { sessions: CouncilSession[] }) {
  return (
    <Card aria-label="Council decision feed">
      <CardHeader
        title="Council decisions"
        subtitle="Build-time, runtime, and review council sessions (ANIF-902–907)"
      />
      <CardBody>
        {sessions.length === 0 ? (
          <p className="text-sm text-chrome-600">No council sessions recorded yet.</p>
        ) : (
          <ul className="divide-y divide-chrome-100">
            {sessions.map((session) => (
              <li key={session.council_id} className="space-y-1 py-2.5">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge>{session.council_type.replace("_", "-")}</Badge>
                  <Badge variant={COUNCIL_DECISION_VARIANT[session.decision] ?? "default"}>
                    {session.decision}
                  </Badge>
                  <time
                    dateTime={session.trigger_timestamp}
                    className="text-xs text-chrome-600"
                  >
                    {new Date(session.trigger_timestamp).toLocaleString()}
                  </time>
                  {session.intent_id && (
                    <Link
                      to={`/audit/${session.intent_id}`}
                      className="font-mono text-xs text-brand-700 hover:underline"
                    >
                      {session.intent_id.slice(0, 8)}…
                    </Link>
                  )}
                </div>
                <p className="text-sm text-chrome-700">{session.triggered_by}</p>
                {session.decision_rationale && (
                  <p className="text-xs text-chrome-600">{session.decision_rationale}</p>
                )}
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  );
}

// ── Ethics strikes log ─────────────────────────────────────────────────────

function StrikesLog({ strikes, total }: { strikes: StrikeRecord[]; total: number }) {
  return (
    <Card aria-label="Ethics strikes log">
      <CardHeader
        title="Ethics strikes"
        subtitle={`Append-only agent strike record — ${total} total (ANIF-721 §7)`}
      />
      <CardBody>
        {strikes.length === 0 ? (
          <p className="text-sm text-chrome-600">
            No strikes recorded. Strikes are appended when an agent violates
            ethics constraints; records are never updated or deleted.
          </p>
        ) : (
          <ul className="divide-y divide-chrome-100">
            {strikes.map((strike) => (
              <li key={strike.strike_id} className="space-y-1 py-2.5">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant={statusVariant("failed")}>strike</Badge>
                  <span className="font-mono text-xs text-chrome-700">
                    agent {strike.agent_id.slice(0, 8)}…
                  </span>
                  <Link
                    to={`/audit/${strike.intent_id}`}
                    className="font-mono text-xs text-brand-700 hover:underline"
                  >
                    intent {strike.intent_id.slice(0, 8)}…
                  </Link>
                  <time dateTime={strike.recorded_at} className="text-xs text-chrome-600">
                    {new Date(strike.recorded_at).toLocaleString()}
                  </time>
                </div>
                <p className="text-sm text-chrome-700">{strike.reason}</p>
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  );
}
