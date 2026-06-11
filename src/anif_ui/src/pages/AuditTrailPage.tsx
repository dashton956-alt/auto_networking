import { Fragment, useCallback, useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { listAuditRecords, type AuditFilters } from "@/api/audit";
import type { AuditRecord } from "@/api/types";
import { PIPELINE_STAGES } from "@/api/types";
import { Alert, Badge, Button, Input, Select, Skeleton, statusVariant } from "@/components";
import { AuditRecordDetail } from "@/components/AuditRecordDetail";

const PAGE_SIZE = 25;

const STAGE_OPTIONS = PIPELINE_STAGES.map((s) => ({ value: s, label: s }));
const OUTCOME_OPTIONS = ["success", "failure", "blocked", "escalated"].map((o) => ({
  value: o,
  label: o,
}));
const ENVIRONMENT_OPTIONS = ["dev", "staging", "prod"].map((e) => ({ value: e, label: e }));

interface FilterFormState {
  stage: string;
  outcome: string;
  environment: string;
  operatorId: string;
  dateFrom: string;
  dateTo: string;
}

const EMPTY_FILTERS: FilterFormState = {
  stage: "",
  outcome: "",
  environment: "",
  operatorId: "",
  dateFrom: "",
  dateTo: "",
};

function toApiFilters(form: FilterFormState, offset: number): AuditFilters {
  return {
    stage: form.stage || undefined,
    outcome: form.outcome || undefined,
    environment: form.environment || undefined,
    operator_id: form.operatorId.trim() || undefined,
    date_from: form.dateFrom ? new Date(form.dateFrom).toISOString() : undefined,
    date_to: form.dateTo ? new Date(form.dateTo).toISOString() : undefined,
    limit: PAGE_SIZE,
    offset,
  };
}

const outcomeVariant = (outcome: string) =>
  outcome === "failure" ? "failed" : statusVariant(outcome);

export default function AuditTrailPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState<FilterFormState>(EMPTY_FILTERS);
  const [applied, setApplied] = useState<FilterFormState>(EMPTY_FILTERS);
  const [offset, setOffset] = useState(0);
  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [timelineId, setTimelineId] = useState("");

  const set = <K extends keyof FilterFormState>(key: K, value: string) =>
    setForm((f) => ({ ...f, [key]: value }));

  const load = useCallback(async (filters: FilterFormState, nextOffset: number) => {
    setLoading(true);
    setError(null);
    setExpanded(null);
    try {
      const data = await listAuditRecords(toApiFilters(filters, nextOffset));
      setRecords(data);
      setOffset(nextOffset);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load audit records");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load(EMPTY_FILTERS, 0);
  }, [load]);

  function onApply(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setApplied(form);
    void load(form, 0);
  }

  function onReset() {
    setForm(EMPTY_FILTERS);
    setApplied(EMPTY_FILTERS);
    void load(EMPTY_FILTERS, 0);
  }

  const mayHaveMore = records.length === PAGE_SIZE;

  return (
    <div className="space-y-4">
      {/* Filters — explicit apply, per ANIF-107 §4.5.2 query parameters */}
      <form
        onSubmit={onApply}
        aria-label="Audit record filters"
        className="rounded-lg border border-chrome-200 bg-white p-4 shadow-card"
      >
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <Select
            label="Stage"
            id="filter-stage"
            options={STAGE_OPTIONS}
            placeholder="any"
            value={form.stage}
            onChange={(e) => set("stage", e.target.value)}
          />
          <Select
            label="Outcome"
            id="filter-outcome"
            options={OUTCOME_OPTIONS}
            placeholder="any"
            value={form.outcome}
            onChange={(e) => set("outcome", e.target.value)}
          />
          <Select
            label="Environment"
            id="filter-environment"
            options={ENVIRONMENT_OPTIONS}
            placeholder="any"
            value={form.environment}
            onChange={(e) => set("environment", e.target.value)}
          />
          <Input
            label="Operator"
            id="filter-operator"
            value={form.operatorId}
            placeholder="any"
            onChange={(e) => set("operatorId", e.target.value)}
          />
          <Input
            label="From"
            id="filter-date-from"
            type="datetime-local"
            value={form.dateFrom}
            onChange={(e) => set("dateFrom", e.target.value)}
          />
          <Input
            label="To"
            id="filter-date-to"
            type="datetime-local"
            value={form.dateTo}
            onChange={(e) => set("dateTo", e.target.value)}
          />
        </div>
        <div className="mt-3 flex flex-wrap items-end justify-between gap-3">
          <div className="flex gap-2">
            <Button type="submit" size="sm">
              Apply filters
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={onReset}>
              Reset
            </Button>
          </div>
          <div className="flex items-end gap-2">
            <Input
              label="Intent ID"
              id="timeline-intent-id"
              value={timelineId}
              placeholder="jump to intent timeline"
              onChange={(e) => setTimelineId(e.target.value)}
              className="w-72"
            />
            <Button
              type="button"
              variant="secondary"
              size="sm"
              disabled={!timelineId.trim()}
              onClick={() => navigate(`/audit/${timelineId.trim()}`)}
            >
              View timeline
            </Button>
          </div>
        </div>
      </form>

      {error && (
        <Alert variant="danger" title="Could not load audit records">
          {error} — is the platform API running?
        </Alert>
      )}

      {/* Expandable records table */}
      <div className="overflow-x-auto rounded-lg border border-chrome-200">
        <table className="min-w-full divide-y divide-chrome-200 text-sm">
          <caption className="sr-only">Audit records</caption>
          <thead className="bg-chrome-50">
            <tr>
              {["", "Timestamp", "Intent", "Stage", "Outcome", "Duration", "Operator"].map(
                (header, i) => (
                  <th
                    key={i}
                    scope="col"
                    className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-chrome-500"
                  >
                    {header || <span className="sr-only">Expand</span>}
                  </th>
                ),
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-chrome-100 bg-white">
            {loading &&
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={`skeleton-${i}`}>
                  <td colSpan={7} className="px-4 py-3">
                    <Skeleton className="h-4 w-full" />
                  </td>
                </tr>
              ))}
            {!loading && records.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-chrome-600">
                  No audit records match the current filters.
                </td>
              </tr>
            )}
            {!loading &&
              records.map((record) => {
                const isOpen = expanded === record.record_id;
                return (
                  <Fragment key={record.record_id}>
                    <tr className={isOpen ? "bg-brand-50/40" : undefined}>
                      <td className="px-4 py-2.5">
                        <button
                          type="button"
                          aria-expanded={isOpen}
                          aria-controls={`detail-${record.record_id}`}
                          aria-label={`${isOpen ? "Collapse" : "Expand"} reasoning for ${record.stage} record`}
                          onClick={() => setExpanded(isOpen ? null : record.record_id)}
                          className="flex h-6 w-6 items-center justify-center rounded text-chrome-600 hover:bg-chrome-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500"
                        >
                          <span aria-hidden="true">{isOpen ? "▾" : "▸"}</span>
                        </button>
                      </td>
                      <td className="whitespace-nowrap px-4 py-2.5">
                        <time dateTime={record.timestamp} className="text-chrome-700">
                          {new Date(record.timestamp).toLocaleString()}
                        </time>
                      </td>
                      <td className="px-4 py-2.5">
                        <Link
                          to={`/audit/${record.intent_id}`}
                          className="font-mono text-xs text-brand-700 hover:underline"
                        >
                          {record.intent_id.slice(0, 8)}…
                        </Link>
                      </td>
                      <td className="px-4 py-2.5">
                        <Badge>{record.stage}</Badge>
                      </td>
                      <td className="px-4 py-2.5">
                        <Badge variant={outcomeVariant(record.outcome)}>{record.outcome}</Badge>
                      </td>
                      <td className="whitespace-nowrap px-4 py-2.5 text-chrome-600">
                        {record.duration_ms} ms
                      </td>
                      <td className="px-4 py-2.5 text-chrome-600">
                        {record.operator_id ?? "—"}
                      </td>
                    </tr>
                    {isOpen && (
                      <tr id={`detail-${record.record_id}`}>
                        <td colSpan={7} className="bg-chrome-50 px-6 py-4">
                          <AuditRecordDetail record={record} />
                        </td>
                      </tr>
                    )}
                  </Fragment>
                );
              })}
          </tbody>
        </table>
      </div>

      <nav aria-label="Audit record pagination" className="flex items-center justify-between">
        <p className="text-sm text-chrome-600">
          Showing {records.length} record{records.length === 1 ? "" : "s"}
          {offset > 0 && ` (from ${offset + 1})`}
        </p>
        <div className="flex gap-2">
          <Button
            variant="secondary"
            size="sm"
            disabled={offset === 0 || loading}
            onClick={() => void load(applied, Math.max(0, offset - PAGE_SIZE))}
          >
            Previous
          </Button>
          <Button
            variant="secondary"
            size="sm"
            disabled={!mayHaveMore || loading}
            onClick={() => void load(applied, offset + PAGE_SIZE)}
          >
            Next
          </Button>
        </div>
      </nav>
    </div>
  );
}
