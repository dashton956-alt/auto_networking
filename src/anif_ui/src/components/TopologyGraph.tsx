import { intentStatus, type TopologyDevice } from "@/api/topology";
import { layoutTopology } from "@/lib/topologyLayout";

/**
 * Intent-status colouring (the F5 intent overlay). Fills are the design
 * tokens; node text is white on the darkened status colours.
 */
const STATUS_FILL: Record<string, string> = {
  success: "#166534",
  pending: "#4b5563",
  failed: "#b91c1c",
};
const DEFAULT_FILL = "#475569"; // chrome-600 — no intent applied

const NODE_W = 124;
const NODE_H = 44;

interface TopologyGraphProps {
  site: string;
  devices: TopologyDevice[];
  connections: [string, string][];
  selected: string | null;
  onSelect: (name: string) => void;
}

/**
 * SVG topology canvas. Mouse users can click nodes; keyboard users get the
 * same selection through the parallel device list rendered by TopologyPage,
 * so the SVG itself is presented as a described image.
 */
export function TopologyGraph({
  site,
  devices,
  connections,
  selected,
  onSelect,
}: TopologyGraphProps) {
  const layout = layoutTopology(devices);

  return (
    <svg
      role="img"
      aria-label={`Network topology for site ${site}: ${devices.length} devices, ${connections.length} links. Node colours show intent status; use the device list to inspect devices.`}
      viewBox={`0 0 ${layout.width} ${layout.height}`}
      className="h-auto w-full rounded-lg border border-chrome-200 bg-white"
    >
      {/* Links */}
      {connections.map(([a, b]) => {
        const from = layout.positions[a];
        const to = layout.positions[b];
        if (!from || !to) return null;
        return (
          <line
            key={`${a}|${b}`}
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke="#cbd5e1"
            strokeWidth={2}
          />
        );
      })}

      {/* Nodes */}
      {devices.map((device) => {
        const pos = layout.positions[device.name];
        if (!pos) return null;
        const status = intentStatus(device);
        const fill = (status && STATUS_FILL[status]) || DEFAULT_FILL;
        const isSelected = device.name === selected;
        return (
          <g
            key={device.name}
            transform={`translate(${pos.x - NODE_W / 2}, ${pos.y - NODE_H / 2})`}
            onClick={() => onSelect(device.name)}
            className="cursor-pointer"
            aria-hidden="true"
          >
            <rect
              width={NODE_W}
              height={NODE_H}
              rx={8}
              fill={fill}
              stroke={isSelected ? "#1d4ed8" : "transparent"}
              strokeWidth={3}
            />
            <text
              x={NODE_W / 2}
              y={18}
              textAnchor="middle"
              fill="#ffffff"
              fontSize="12"
              fontWeight="600"
            >
              {device.name}
            </text>
            <text x={NODE_W / 2} y={33} textAnchor="middle" fill="#e2e8f0" fontSize="10">
              {device.role}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
