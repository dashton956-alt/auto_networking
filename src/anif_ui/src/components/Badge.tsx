type Variant =
  | "default"
  | "success"
  | "warning"
  | "danger"
  | "info"
  | "pending"
  | "running"
  | "failed"
  | "blocked"
  | "escalated"
  | "cancelled";

interface BadgeProps {
  variant?: Variant;
  children: React.ReactNode;
  className?: string;
}

const variantClasses: Record<Variant, string> = {
  default: "bg-chrome-100 text-chrome-700",
  success: "bg-status-success-bg text-status-success border border-status-success-border",
  warning: "bg-status-warning-bg text-status-warning border border-status-warning-border",
  danger: "bg-status-danger-bg text-status-danger border border-status-danger-border",
  info: "bg-status-info-bg text-status-info border border-status-info-border",
  pending: "bg-chrome-100 text-intent-pending",
  running: "bg-brand-50 text-intent-running",
  failed: "bg-status-danger-bg text-intent-failed border border-status-danger-border",
  blocked: "bg-orange-50 text-intent-blocked border border-orange-200",
  escalated: "bg-violet-50 text-intent-escalated border border-violet-200",
  cancelled: "bg-chrome-100 text-intent-cancelled",
};

export function Badge({ variant = "default", children, className = "" }: BadgeProps) {
  return (
    <span
      className={[
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
        variantClasses[variant],
        className,
      ].join(" ")}
    >
      {children}
    </span>
  );
}

/** Maps an intent/ticket status string to the correct Badge variant. */
export function statusVariant(status: string): Variant {
  const map: Record<string, Variant> = {
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
