import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { listIntents } from "@/api/intents";
import type { ValidatedIntent } from "@/api/types";
import { Alert, Badge, Button, Table, statusVariant } from "@/components";

const PAGE_SIZE = 20;

export default function IntentListPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<ValidatedIntent[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (nextOffset: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await listIntents({ limit: PAGE_SIZE, offset: nextOffset });
      setItems(response.items);
      setTotal(response.total);
      setOffset(nextOffset);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load intents");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load(0);
  }, [load]);

  const pageEnd = Math.min(offset + PAGE_SIZE, total);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-chrome-600">
          Registered intents, newest first
          {total > 0 && (
            <span>
              {" "}
              — showing {offset + 1}–{pageEnd} of {total}
            </span>
          )}
        </p>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => void load(offset)}>
            Refresh
          </Button>
          <Button size="sm" onClick={() => navigate("/intents/new")}>
            New Intent
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="danger" title="Could not load intents">
          {error} — is the platform API running?
        </Alert>
      )}

      <Table<ValidatedIntent>
        caption="Registered intents"
        columns={[
          {
            key: "change_number",
            header: "Change #",
            width: "6rem",
            render: (row) => <span className="font-mono text-chrome-600">{row.change_number}</span>,
          },
          {
            key: "service",
            header: "Service",
            render: (row) => (
              <Link
                to={`/intents/${row.intent_id}`}
                className="font-medium text-brand-700 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500"
              >
                {row.service}
              </Link>
            ),
          },
          {
            key: "environment",
            header: "Environment",
            render: (row) => (
              <span className="text-chrome-600">
                {String(row.resolved_intent.environment ?? "—")}
              </span>
            ),
          },
          {
            key: "status",
            header: "Status",
            render: (row) => <Badge variant={statusVariant(row.status)}>{row.status}</Badge>,
          },
          {
            key: "warnings",
            header: "Warnings",
            width: "6rem",
            render: (row) =>
              row.warnings.length > 0 ? (
                <Badge variant="warning">{row.warnings.length}</Badge>
              ) : (
                <span className="text-chrome-500">0</span>
              ),
          },
          {
            key: "created_at",
            header: "Created",
            render: (row) => (
              <time dateTime={row.created_at} className="text-chrome-600">
                {new Date(row.created_at).toLocaleString()}
              </time>
            ),
          },
        ]}
        rows={items}
        rowKey={(row) => row.intent_id}
        loading={loading}
        emptyMessage="No intents registered yet. Submit one to get started."
      />

      {total > PAGE_SIZE && (
        <nav aria-label="Intent list pagination" className="flex justify-end gap-2">
          <Button
            variant="secondary"
            size="sm"
            disabled={offset === 0 || loading}
            onClick={() => void load(Math.max(0, offset - PAGE_SIZE))}
          >
            Previous
          </Button>
          <Button
            variant="secondary"
            size="sm"
            disabled={pageEnd >= total || loading}
            onClick={() => void load(offset + PAGE_SIZE)}
          >
            Next
          </Button>
        </nav>
      )}
    </div>
  );
}
