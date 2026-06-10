import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  "aria-label"?: string;
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}

export function Card({ children, className = "", "aria-label": label }: CardProps) {
  return (
    <section
      aria-label={label}
      className={["bg-white rounded-lg shadow-card border border-chrome-200", className].join(" ")}
    >
      {children}
    </section>
  );
}

export function CardHeader({ title, subtitle, action }: CardHeaderProps) {
  return (
    <div className="flex items-start justify-between px-5 py-4 border-b border-chrome-200">
      <div>
        <h2 className="text-sm font-semibold text-chrome-900">{title}</h2>
        {subtitle && <p className="mt-0.5 text-xs text-chrome-500">{subtitle}</p>}
      </div>
      {action && <div className="ml-4 shrink-0">{action}</div>}
    </div>
  );
}

export function CardBody({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={["px-5 py-4", className].join(" ")}>{children}</div>;
}

export function CardFooter({ children }: { children: ReactNode }) {
  return (
    <div className="px-5 py-3 border-t border-chrome-200 bg-chrome-50 rounded-b-lg flex items-center justify-end gap-2">
      {children}
    </div>
  );
}
