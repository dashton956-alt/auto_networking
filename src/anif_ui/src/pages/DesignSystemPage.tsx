import { useState } from "react";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  CountdownTimer,
  Input,
  RiskBadge,
  RiskMeter,
  Select,
  Skeleton,
  SkeletonText,
  Spinner,
  Table,
  statusVariant,
} from "@/components";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section aria-labelledby={`section-${title.toLowerCase().replace(/\s/g, "-")}`}>
      <h2
        id={`section-${title.toLowerCase().replace(/\s/g, "-")}`}
        className="text-xs font-semibold text-chrome-500 uppercase tracking-widest mb-4 pb-2 border-b border-chrome-200"
      >
        {title}
      </h2>
      <div className="space-y-4">{children}</div>
    </section>
  );
}

const INTENTS = [
  { id: "1", service: "bgp-reroute", status: "success", risk: 22 },
  { id: "2", service: "qos-policy", status: "pending", risk: 48 },
  { id: "3", service: "isolate-segment", status: "blocked", risk: 91 },
  { id: "4", service: "scale-bandwidth", status: "running", risk: 35 },
];

export default function DesignSystemPage() {
  const [inputVal, setInputVal] = useState("");
  const [inputError, setInputError] = useState("");
  const [dismissed, setDismissed] = useState(false);
  const expiresAt = new Date(Date.now() + 8 * 60 * 1000); // 8 min from now

  return (
    <div className="max-w-4xl mx-auto space-y-12 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-chrome-900">Design System</h1>
        <p className="mt-1 text-sm text-chrome-500">ANIF Platform component library — F1</p>
      </div>

      {/* Buttons */}
      <Section title="Buttons">
        <div className="flex flex-wrap gap-3 items-center">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="danger">Danger</Button>
          <Button variant="ghost">Ghost</Button>
        </div>
        <div className="flex flex-wrap gap-3 items-center">
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
        </div>
        <div className="flex flex-wrap gap-3 items-center">
          <Button loading>Loading</Button>
          <Button disabled>Disabled</Button>
        </div>
      </Section>

      {/* Badges */}
      <Section title="Badges">
        <div className="flex flex-wrap gap-2 items-center">
          {(["success", "warning", "danger", "info", "pending", "running", "failed", "blocked", "escalated", "cancelled"] as const).map(
            (v) => <Badge key={v} variant={v}>{v}</Badge>,
          )}
        </div>
        <div className="flex flex-wrap gap-2 items-center">
          <p className="text-xs text-chrome-500">via statusVariant():</p>
          {["success", "failed", "pending", "blocked", "approved", "rejected"].map((s) => (
            <Badge key={s} variant={statusVariant(s)}>{s}</Badge>
          ))}
        </div>
      </Section>

      {/* Alerts */}
      <Section title="Alerts">
        <Alert variant="success" title="Action completed">
          The BGP reroute intent executed successfully and rollback is available.
        </Alert>
        <Alert variant="warning" title="Approval required">
          This action has risk score 72 and requires senior engineer approval.
        </Alert>
        <Alert variant="danger" title="Execution failed">
          The apply_qos action failed. Automatic rollback was attempted.
        </Alert>
        {!dismissed && (
          <Alert variant="info" onDismiss={() => setDismissed(true)}>
            You have 3 pending approval tickets.
          </Alert>
        )}
      </Section>

      {/* Risk Meter */}
      <Section title="Risk Meter">
        <div className="space-y-3 max-w-xs">
          {[15, 50, 88].map((score) => (
            <div key={score} className="flex items-center gap-4">
              <span className="text-xs text-chrome-500 w-12">Score {score}</span>
              <RiskMeter score={score} className="flex-1" />
            </div>
          ))}
        </div>
        <div className="flex gap-4">
          <RiskBadge score={15} />
          <RiskBadge score={55} />
          <RiskBadge score={85} />
        </div>
      </Section>

      {/* Countdown Timer */}
      <Section title="Countdown Timer">
        <div className="flex items-center gap-3">
          <span className="text-sm text-chrome-600">Ticket expires in:</span>
          <CountdownTimer expiresAt={expiresAt} />
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-chrome-600">Urgent (&lt;2 min):</span>
          <CountdownTimer expiresAt={new Date(Date.now() + 90 * 1000)} />
        </div>
      </Section>

      {/* Forms */}
      <Section title="Form Inputs">
        <div className="grid grid-cols-2 gap-4 max-w-lg">
          <Input
            label="Intent ID"
            value={inputVal}
            onChange={(e) => {
              setInputVal(e.target.value);
              setInputError(e.target.value.length < 3 && e.target.value.length > 0 ? "Too short" : "");
            }}
            placeholder="intent-abc-123"
            helperText="Enter the intent UUID or short ID"
            error={inputError}
          />
          <Select
            label="Environment"
            options={[
              { value: "dev", label: "Development" },
              { value: "staging", label: "Staging" },
              { value: "prod", label: "Production" },
            ]}
            placeholder="Select environment"
          />
        </div>
      </Section>

      {/* Table */}
      <Section title="Table">
        <Table
          caption="Recent intents"
          rowKey={(r) => r.id}
          columns={[
            { key: "id", header: "ID", render: (r) => <code className="text-xs font-mono">{r.id}</code> },
            { key: "service", header: "Service", render: (r) => r.service },
            {
              key: "status",
              header: "Status",
              render: (r) => <Badge variant={statusVariant(r.status)}>{r.status}</Badge>,
            },
            {
              key: "risk",
              header: "Risk",
              render: (r) => <RiskMeter score={r.risk} className="w-28" />,
            },
          ]}
          rows={INTENTS}
        />
        <Table<{ id: string; service: string }>
          caption="Loading state"
          rowKey={(r) => r.id}
          columns={[
            { key: "id", header: "ID", render: (r) => r.id },
            { key: "service", header: "Service", render: (r) => r.service },
          ]}
          rows={[]}
          loading
        />
        <Table
          caption="Empty state"
          rowKey={(r: { id: string }) => r.id}
          columns={[
            { key: "id", header: "ID", render: (r: { id: string }) => r.id },
          ]}
          rows={[]}
          emptyMessage="No intents found matching your filter."
        />
      </Section>

      {/* Card */}
      <Section title="Card">
        <Card aria-label="Example card">
          <CardHeader
            title="Approval Ticket #T-042"
            subtitle="Submitted 5 minutes ago"
            action={<Badge variant="pending">Pending</Badge>}
          />
          <CardBody>
            <p className="text-sm text-chrome-700">
              isolate_segment request for segment-prod-4b. Risk score: 82. Requires senior
              engineer approval before execution.
            </p>
          </CardBody>
          <CardFooter>
            <Button variant="secondary" size="sm">Reject</Button>
            <Button variant="primary" size="sm">Approve</Button>
          </CardFooter>
        </Card>
      </Section>

      {/* Spinner */}
      <Section title="Spinner">
        <div className="flex gap-6 items-center">
          <Spinner size="sm" />
          <Spinner size="md" />
          <Spinner size="lg" />
          <Spinner size="md" className="text-brand-600" aria-label="Loading intents" />
        </div>
      </Section>

      {/* Skeleton */}
      <Section title="Skeleton">
        <div className="max-w-sm space-y-3">
          <Skeleton className="h-8 w-48" aria-label="Loading title" />
          <SkeletonText lines={4} />
        </div>
      </Section>
    </div>
  );
}
