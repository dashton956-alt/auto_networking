/**
 * Deterministic layered layout for the topology graph: devices are grouped
 * by role, roles are stacked in conventional network order (core at the
 * top, hosts at the bottom), and each row is spread across the width.
 */

import type { TopologyDevice } from "@/api/topology";

export interface NodePosition {
  x: number;
  y: number;
}

export interface TopologyLayout {
  width: number;
  height: number;
  positions: Record<string, NodePosition>;
}

const ROLE_ORDER = ["core", "spine", "distribution", "leaf", "access", "server", "host"];

const ROW_HEIGHT = 120;
const MIN_WIDTH = 720;
const PADDING_Y = 56;

function roleRank(role: string): number {
  const index = ROLE_ORDER.indexOf(role.toLowerCase());
  return index === -1 ? ROLE_ORDER.length : index;
}

export function layoutTopology(devices: TopologyDevice[]): TopologyLayout {
  const byRole = new Map<string, TopologyDevice[]>();
  for (const device of devices) {
    const group = byRole.get(device.role) ?? [];
    group.push(device);
    byRole.set(device.role, group);
  }

  const roles = [...byRole.keys()].sort(
    (a, b) => roleRank(a) - roleRank(b) || a.localeCompare(b),
  );

  const widest = Math.max(1, ...[...byRole.values()].map((group) => group.length));
  const width = Math.max(MIN_WIDTH, widest * 160);
  const height = Math.max(1, roles.length) * ROW_HEIGHT + PADDING_Y;

  const positions: Record<string, NodePosition> = {};
  roles.forEach((role, rowIndex) => {
    const group = [...(byRole.get(role) ?? [])].sort((a, b) => a.name.localeCompare(b.name));
    group.forEach((device, colIndex) => {
      positions[device.name] = {
        x: ((colIndex + 1) * width) / (group.length + 1),
        y: PADDING_Y + rowIndex * ROW_HEIGHT,
      };
    });
  });

  return { width, height, positions };
}
