import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { orchestrate, validateIntent } from "@/api/intents";
import type { IntentDraft, OrchestrateResponse, ValidationResult } from "@/api/types";
import { Alert, Button, Card, CardBody, CardHeader, Input, Select } from "@/components";
import { PipelineStatusTracker } from "@/components/PipelineStatusTracker";
import { stagesFromOrchestrate } from "@/lib/pipelineStages";

const ENVIRONMENTS = [
  { value: "dev", label: "dev" },
  { value: "staging", label: "staging" },
  { value: "prod", label: "prod" },
];

const PRIORITIES = [
  { value: "low", label: "low" },
  { value: "medium", label: "medium" },
  { value: "high", label: "high" },
  { value: "critical", label: "critical" },
];

const REGIONS = [
  { value: "EU", label: "EU" },
  { value: "US", label: "US" },
  { value: "APAC", label: "APAC" },
];

const POLICIES = ["zero_trust", "no_public_ingress", "pci_compliant", "data_residency"];

type Action = "validate" | "dry_run" | "submit";

interface FormState {
  service: string;
  environment: string;
  priority: string;
  latencyMs: string;
  availabilityPercent: string;
  throughputMbps: string;
  region: string;
  encryption: boolean;
  allowedZones: string;
  policies: string[];
}

const INITIAL_FORM: FormState = {
  service: "",
  environment: "",
  priority: "",
  latencyMs: "",
  availabilityPercent: "",
  throughputMbps: "",
  region: "",
  encryption: false,
  allowedZones: "",
  policies: [],
};

function buildDraft(form: FormState): IntentDraft {
  const draft: IntentDraft = {
    service: form.service.trim(),
    objectives: {},
    constraints: {},
  };
  if (form.environment) draft.environment = form.environment;
  if (form.priority) draft.priority = form.priority;
  if (form.latencyMs) draft.objectives.latency_ms = Number(form.latencyMs);
  if (form.availabilityPercent)
    draft.objectives.availability_percent = Number(form.availabilityPercent);
  if (form.throughputMbps) draft.objectives.throughput_mbps = Number(form.throughputMbps);
  if (form.region) draft.constraints.region = form.region;
  if (form.encryption) draft.constraints.encryption = true;
  const zones = form.allowedZones
    .split(",")
    .map((z) => z.trim())
    .filter(Boolean);
  if (zones.length > 0) draft.constraints.allowed_zones = zones;
  if (form.policies.length > 0) draft.policies = form.policies;
  return draft;
}

export default function IntentSubmitPage() {
  const [form, setForm] = useState<FormState>(INITIAL_FORM);
  const [busy, setBusy] = useState<Action | null>(null);
  const [requestError, setRequestError] = useState<string | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [orchestration, setOrchestration] = useState<OrchestrateResponse | null>(null);

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const togglePolicy = (policy: string) =>
    setForm((f) => ({
      ...f,
      policies: f.policies.includes(policy)
        ? f.policies.filter((p) => p !== policy)
        : [...f.policies, policy],
    }));

  const serviceError =
    form.service.trim() === "" && (validation || orchestration)
      ? "Service name is required"
      : undefined;

  async function run(action: Action) {
    setBusy(action);
    setRequestError(null);
    setValidation(null);
    setOrchestration(null);
    try {
      const draft = buildDraft(form);
      if (action === "validate") {
        setValidation(await validateIntent(draft));
      } else {
        setOrchestration(await orchestrate(draft, action === "dry_run"));
      }
    } catch (err) {
      setRequestError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setBusy(null);
    }
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void run("submit");
  }

  return (
    <div className="max-w-3xl space-y-4">
      <Card aria-label="Intent submission form">
        <CardHeader
          title="Submit a network intent"
          subtitle="Declarative statement of what the service must achieve (ANIF-300)"
        />
        <CardBody>
          <form onSubmit={onSubmit} noValidate className="space-y-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <Input
                label="Service"
                required
                value={form.service}
                error={serviceError}
                placeholder="payments"
                onChange={(e) => set("service", e.target.value)}
              />
              <Select
                label="Environment"
                options={ENVIRONMENTS}
                placeholder="default (dev)"
                value={form.environment}
                onChange={(e) => set("environment", e.target.value)}
              />
              <Select
                label="Priority"
                options={PRIORITIES}
                placeholder="default (medium)"
                value={form.priority}
                onChange={(e) => set("priority", e.target.value)}
                helperText="prod requires high or critical"
              />
            </div>

            <fieldset className="space-y-4">
              <legend className="text-sm font-semibold text-chrome-900">Objectives</legend>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <Input
                  label="Latency (ms)"
                  type="number"
                  min="1"
                  step="any"
                  value={form.latencyMs}
                  onChange={(e) => set("latencyMs", e.target.value)}
                />
                <Input
                  label="Availability (%)"
                  type="number"
                  min="90"
                  max="100"
                  step="any"
                  value={form.availabilityPercent}
                  onChange={(e) => set("availabilityPercent", e.target.value)}
                  helperText="99.99+ needs 2+ zones"
                />
                <Input
                  label="Throughput (Mbps)"
                  type="number"
                  min="0"
                  step="any"
                  value={form.throughputMbps}
                  onChange={(e) => set("throughputMbps", e.target.value)}
                />
              </div>
            </fieldset>

            <fieldset className="space-y-4">
              <legend className="text-sm font-semibold text-chrome-900">Constraints</legend>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <Select
                  label="Region"
                  options={REGIONS}
                  placeholder="none"
                  value={form.region}
                  onChange={(e) => set("region", e.target.value)}
                />
                <Input
                  label="Allowed zones"
                  value={form.allowedZones}
                  placeholder="zone-a, zone-b"
                  onChange={(e) => set("allowedZones", e.target.value)}
                  helperText="Comma-separated"
                />
                <div className="flex items-end pb-2">
                  <label className="flex items-center gap-2 text-sm text-chrome-700">
                    <input
                      type="checkbox"
                      checked={form.encryption}
                      onChange={(e) => set("encryption", e.target.checked)}
                      className="h-4 w-4 rounded border-chrome-300 text-brand-600 focus:ring-brand-500"
                    />
                    Encryption required
                  </label>
                </div>
              </div>
            </fieldset>

            <fieldset>
              <legend className="text-sm font-semibold text-chrome-900">Policies</legend>
              <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                {POLICIES.map((policy) => (
                  <label
                    key={policy}
                    className="flex items-center gap-2 text-sm text-chrome-700"
                  >
                    <input
                      type="checkbox"
                      checked={form.policies.includes(policy)}
                      onChange={() => togglePolicy(policy)}
                      className="h-4 w-4 rounded border-chrome-300 text-brand-600 focus:ring-brand-500"
                    />
                    {policy}
                  </label>
                ))}
              </div>
            </fieldset>

            <div className="flex flex-wrap gap-2 border-t border-chrome-100 pt-4">
              <Button
                type="button"
                variant="secondary"
                loading={busy === "validate"}
                disabled={busy !== null}
                onClick={() => void run("validate")}
              >
                Validate only
              </Button>
              <Button
                type="button"
                variant="secondary"
                loading={busy === "dry_run"}
                disabled={busy !== null}
                onClick={() => void run("dry_run")}
              >
                Dry run
              </Button>
              <Button type="submit" loading={busy === "submit"} disabled={busy !== null}>
                Submit intent
              </Button>
            </div>
          </form>
        </CardBody>
      </Card>

      <div aria-live="polite" className="space-y-4">
        {requestError && (
          <Alert variant="danger" title="Request failed">
            {requestError}
          </Alert>
        )}

        {validation && (
          <Card aria-label="Validation result">
            <CardHeader title="Validation result" />
            <CardBody className="space-y-3">
              {validation.status === "validated" ? (
                <Alert variant="success" title="Intent is valid">
                  Assigned intent ID:{" "}
                  <span className="font-mono">{validation.intent_id}</span>
                </Alert>
              ) : (
                <Alert variant="danger" title="Validation failed">
                  <ul className="list-disc pl-4">
                    {validation.errors.map((e) => (
                      <li key={e}>{e}</li>
                    ))}
                  </ul>
                </Alert>
              )}
              {validation.warnings.map((w) => (
                <Alert key={w} variant="warning">
                  {w}
                </Alert>
              ))}
            </CardBody>
          </Card>
        )}

        {orchestration && <OrchestrationResult result={orchestration} />}
      </div>
    </div>
  );
}

function OrchestrationResult({ result }: { result: OrchestrateResponse }) {
  const states = stagesFromOrchestrate(result);

  return (
    <Card aria-label="Pipeline result">
      <CardHeader
        title={result.dry_run ? "Dry run result" : "Pipeline result"}
        subtitle={result.intent_id ? `Intent ${result.intent_id}` : undefined}
      />
      <CardBody className="space-y-4">
        <PipelineStatusTracker states={states} />

        {result.status === "pipeline_complete" && !result.dry_run && (
          <Alert variant="success" title="Pipeline complete">
            Intent executed successfully.{" "}
            {result.intent_id && (
              <Link className="font-medium underline" to={`/intents/${result.intent_id}`}>
                View intent details
              </Link>
            )}
          </Alert>
        )}

        {result.status === "pipeline_complete" && result.dry_run && (
          <Alert variant="info" title="Dry run complete">
            All stages evaluated; nothing was executed.
          </Alert>
        )}

        {result.status === "pending_approval" && (
          <Alert variant="warning" title="Pending human approval">
            Governance routed this intent to manual review. Ticket{" "}
            <span className="font-mono">{result.ticket_id}</span>
            {result.ticket_expires_at && (
              <> — expires {new Date(result.ticket_expires_at).toLocaleString()}</>
            )}
            .{" "}
            {result.intent_id && (
              <Link className="font-medium underline" to={`/intents/${result.intent_id}`}>
                View intent details
              </Link>
            )}
          </Alert>
        )}

        {(result.status === "failed" || result.status === "precondition_failed") && (
          <Alert variant="danger" title={`Failed at ${result.stage ?? "unknown"} stage`}>
            {result.errors?.length ? (
              <ul className="list-disc pl-4">
                {result.errors.map((e) => (
                  <li key={e}>{e}</li>
                ))}
              </ul>
            ) : (
              (result.error ?? "The pipeline rejected this intent.")
            )}
          </Alert>
        )}

        {result.status === "blocked" && (
          <Alert variant="danger" title={`Blocked at ${result.stage ?? "unknown"} stage`}>
            The {result.stage} stage blocked this intent from proceeding.
          </Alert>
        )}

        {result.warnings && result.warnings.length > 0 && (
          <Alert variant="warning" title="Warnings">
            <ul className="list-disc pl-4">
              {result.warnings.map((w) => (
                <li key={w}>{w}</li>
              ))}
            </ul>
          </Alert>
        )}
      </CardBody>
    </Card>
  );
}
