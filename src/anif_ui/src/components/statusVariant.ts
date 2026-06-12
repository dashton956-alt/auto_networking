import type { BadgeVariant } from "./Badge";

/** Maps an intent/ticket status string to the correct Badge variant. */
export function statusVariant(status: string): BadgeVariant {
  const map: Record<string, BadgeVariant> = {
    success: "success",
    failed: "failed",
    pending: "pending",
    running: "running",
    blocked: "blocked",
    escalated: "escalated",
    cancelled: "cancelled",
    approved: "success",
    rejected: "danger",
  };
  return map[status.toLowerCase()] ?? "default";
}
