import type { ReactNode } from "react";

type Variant = "success" | "warning" | "danger" | "info";

interface AlertProps {
  variant?: Variant;
  title?: string;
  children: ReactNode;
  onDismiss?: () => void;
}

const styles: Record<Variant, { wrapper: string; icon: string }> = {
  success: {
    wrapper: "bg-status-success-bg border-status-success-border text-status-success",
    icon: "✓",
  },
  warning: {
    wrapper: "bg-status-warning-bg border-status-warning-border text-status-warning",
    icon: "⚠",
  },
  danger: {
    wrapper: "bg-status-danger-bg border-status-danger-border text-status-danger",
    icon: "✕",
  },
  info: {
    wrapper: "bg-status-info-bg border-status-info-border text-status-info",
    icon: "ℹ",
  },
};

export function Alert({ variant = "info", title, children, onDismiss }: AlertProps) {
  const s = styles[variant];
  return (
    <div
      role="alert"
      className={["flex gap-3 rounded-md border px-4 py-3 text-sm", s.wrapper].join(" ")}
    >
      <span aria-hidden="true" className="shrink-0 font-bold">
        {s.icon}
      </span>
      <div className="flex-1 min-w-0">
        {title && <p className="font-semibold mb-0.5">{title}</p>}
        <div className="text-sm opacity-90">{children}</div>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          aria-label="Dismiss alert"
          className="shrink-0 opacity-60 hover:opacity-100 transition-opacity text-base leading-none"
        >
          ×
        </button>
      )}
    </div>
  );
}
