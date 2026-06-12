import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listTickets, type TicketSummary } from "@/api/governance";
import { Alert, Button, CountdownTimer, RiskBadge, Table } from "@/components";

export default function ApprovalQueuePage() {
  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listTickets();
      setTickets(response.tickets);
      setPendingCount(response.pending_count);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tickets");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-chrome-600">
          {pendingCount === 0
            ? "No tickets awaiting review"
            : `${pendingCount} ticket${pendingCount === 1 ? "" : "s"} awaiting senior_engineer review`}
        </p>
        <Button variant="secondary" size="sm" onClick={() => void load()}>
          Refresh
        </Button>
      </div>

      {pendingCount > 5 && (
        <Alert variant="warning" title="Queue depth high">
          More than 5 tickets are pending — this may indicate staffing or threshold
          calibration issues (ANIF-404 §7).
        </Alert>
      )}

      {error && (
        <Alert variant="danger" title="Could not load approval queue">
          {error} — is the platform API running?
        </Alert>
      )}

      <Table<TicketSummary>
        caption="Pending approval tickets"
        columns={[
          {
            key: "ticket_id",
            header: "Ticket",
            render: (row) => (
              <Link
                to={`/approvals/${row.ticket_id}`}
                className="font-mono text-xs font-medium text-brand-700 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500"
              >
                {row.ticket_id}
              </Link>
            ),
          },
          {
            key: "decision_summary",
            header: "Summary",
            render: (row) => <span className="text-chrome-700">{row.decision_summary}</span>,
          },
          {
            key: "risk_score",
            header: "Risk",
            width: "6rem",
            render: (row) => <RiskBadge score={row.risk_score} />,
          },
          {
            key: "requested_by",
            header: "Requested by",
            render: (row) => <span className="text-chrome-600">{row.requested_by}</span>,
          },
          {
            key: "expires_at",
            header: "Expires in",
            width: "8rem",
            render: (row) => <CountdownTimer expiresAt={row.expires_at} />,
          },
          {
            key: "review",
            header: "Action",
            width: "7rem",
            render: (row) => (
              <Link
                to={`/approvals/${row.ticket_id}`}
                className="inline-flex items-center rounded-md border border-chrome-200 bg-white px-3 py-1.5 text-xs font-medium text-chrome-700 hover:bg-chrome-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500"
              >
                Review
              </Link>
            ),
          },
        ]}
        rows={tickets}
        rowKey={(row) => row.ticket_id}
        loading={loading}
        emptyMessage="No pending tickets. Intents routed to manual review will appear here."
      />
    </div>
  );
}
