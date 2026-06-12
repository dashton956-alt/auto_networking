import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getTopology,
  intentStatus,
  type TopologyDevice,
  type TopologyResponse,
} from "@/api/topology";
import { Alert, Badge, Button, Card, CardBody, CardHeader, SkeletonText } from "@/components";
import { TopologyGraph } from "@/components/TopologyGraph";

const STATUS_BADGE: Record<string, "success" | "pending" | "failed"> = {
  success: "success",
  pending: "pending",
  failed: "failed",
};

const LEGEND: Array<{ swatch: string; label: string }> = [
  { swatch: "#166534", label: "intent applied (success)" },
  { swatch: "#4b5563", label: "intent pending" },
  { swatch: "#b91c1c", label: "intent failed" },
  { swatch: "#475569", label: "no intent metadata" },
];

export default function TopologyPage() {
  const [topology, setTopology] = useState<TopologyResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getTopology();
      setTopology(data);
      setSelected((current) => current ?? data.devices[0]?.name ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load topology");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) {
    return (
      <div className="space-y-4" aria-busy="true">
        <SkeletonText lines={8} />
      </div>
    );
  }

  if (error || !topology) {
    return (
      <Alert variant="danger" title="Could not load topology">
        {error ?? "Unknown error"} — is the platform API running with a configured SoT
        backend (SOT_BACKEND)?
      </Alert>
    );
  }

  const selectedDevice =
    topology.devices.find((device) => device.name === selected) ?? null;
  const neighbours = selectedDevice
    ? topology.connections
        .filter(([a, b]) => a === selectedDevice.name || b === selectedDevice.name)
        .map(([a, b]) => (a === selectedDevice.name ? b : a))
    : [];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-chrome-600">
          Site <span className="font-semibold text-chrome-900">{topology.site}</span> —{" "}
          {topology.devices.length} devices, {topology.connections.length} links (source of
          truth: read-only; intent metadata via write-back)
        </p>
        <Button variant="secondary" size="sm" onClick={() => void load()}>
          Refresh
        </Button>
      </div>

      {/* Intent overlay legend */}
      <ul aria-label="Intent status legend" className="flex flex-wrap gap-x-5 gap-y-1">
        {LEGEND.map((item) => (
          <li key={item.label} className="flex items-center gap-1.5 text-xs text-chrome-700">
            <span
              aria-hidden="true"
              className="inline-block h-3 w-3 rounded"
              style={{ backgroundColor: item.swatch }}
            />
            {item.label}
          </li>
        ))}
      </ul>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <TopologyGraph
            site={topology.site}
            devices={topology.devices}
            connections={topology.connections}
            selected={selected}
            onSelect={setSelected}
          />

          {/* Accessible parallel selection path for the SVG canvas */}
          <nav aria-label="Devices" className="mt-3 flex flex-wrap gap-2">
            {topology.devices.map((device) => {
              const status = intentStatus(device);
              return (
                <button
                  key={device.name}
                  type="button"
                  aria-pressed={device.name === selected}
                  onClick={() => setSelected(device.name)}
                  className={[
                    "rounded-md border px-3 py-1.5 text-xs font-medium transition-colors",
                    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500",
                    device.name === selected
                      ? "border-brand-600 bg-brand-50 text-brand-800"
                      : "border-chrome-200 bg-white text-chrome-700 hover:bg-chrome-50",
                  ].join(" ")}
                >
                  {device.name}
                  {status && (
                    <span className="sr-only"> — intent status {status}</span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Device + interface detail cards */}
        <div className="space-y-4">
          {selectedDevice ? (
            <DeviceDetail device={selectedDevice} neighbours={neighbours} />
          ) : (
            <Card aria-label="Device details">
              <CardBody>
                <p className="text-sm text-chrome-600">Select a device to inspect it.</p>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

function DeviceDetail({
  device,
  neighbours,
}: {
  device: TopologyDevice;
  neighbours: string[];
}) {
  const status = intentStatus(device);
  const lastIntentId = device.custom_fields.last_intent_id || undefined;
  const appliedAt = device.custom_fields.intent_applied_at || undefined;

  return (
    <>
      <Card aria-label={`Device ${device.name}`}>
        <CardHeader
          title={device.name}
          subtitle={`${device.role} · ${device.platform}`}
          action={
            status ? (
              <Badge variant={STATUS_BADGE[status] ?? "default"}>{status}</Badge>
            ) : (
              <Badge>no intent</Badge>
            )
          }
        />
        <CardBody>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between gap-3">
              <dt className="font-medium text-chrome-500">Primary IP</dt>
              <dd className="font-mono text-chrome-900">{device.primary_ip ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-3">
              <dt className="font-medium text-chrome-500">Connected to</dt>
              <dd className="text-right text-chrome-900">
                {neighbours.length > 0 ? neighbours.join(", ") : "—"}
              </dd>
            </div>
            {device.tags.length > 0 && (
              <div className="flex justify-between gap-3">
                <dt className="font-medium text-chrome-500">Tags</dt>
                <dd className="flex flex-wrap justify-end gap-1">
                  {device.tags.map((tag) => (
                    <Badge key={tag}>{tag}</Badge>
                  ))}
                </dd>
              </div>
            )}
            {lastIntentId && (
              <div className="flex justify-between gap-3">
                <dt className="font-medium text-chrome-500">Last intent</dt>
                <dd>
                  <Link
                    to={`/audit/${lastIntentId}`}
                    className="font-mono text-xs text-brand-700 hover:underline"
                  >
                    {lastIntentId.slice(0, 8)}…
                  </Link>
                </dd>
              </div>
            )}
            {appliedAt && (
              <div className="flex justify-between gap-3">
                <dt className="font-medium text-chrome-500">Intent applied</dt>
                <dd>
                  <time dateTime={appliedAt} className="text-chrome-900">
                    {new Date(appliedAt).toLocaleString()}
                  </time>
                </dd>
              </div>
            )}
          </dl>
        </CardBody>
      </Card>

      <Card aria-label={`Interfaces of ${device.name}`}>
        <CardHeader
          title="Interfaces"
          subtitle={`${device.interfaces.length} interface${device.interfaces.length === 1 ? "" : "s"}`}
        />
        <CardBody>
          {device.interfaces.length === 0 ? (
            <p className="text-sm text-chrome-600">No interfaces recorded.</p>
          ) : (
            <ul className="divide-y divide-chrome-100">
              {device.interfaces.map((iface) => (
                <li key={iface.name} className="flex items-center justify-between gap-3 py-2">
                  <span className="font-mono text-sm font-medium text-chrome-900">
                    {iface.name}
                  </span>
                  <span className="flex items-center gap-2">
                    {iface.tags.map((tag) => (
                      <Badge key={tag}>{tag}</Badge>
                    ))}
                    <span className="font-mono text-xs text-chrome-600">
                      {iface.ip_address ?? "unassigned"}
                    </span>
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </>
  );
}
