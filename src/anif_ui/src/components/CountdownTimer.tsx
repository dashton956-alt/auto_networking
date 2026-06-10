import { useEffect, useMemo, useState } from "react";

/** Live countdown to a future date — ANIF-404 §4.7: time remaining before expiry. */

interface CountdownTimerProps {
  expiresAt: Date | string;
  onExpired?: () => void;
  className?: string;
}

function formatRemaining(ms: number): { text: string; urgent: boolean } {
  if (ms <= 0) return { text: "Expired", urgent: true };
  const totalSeconds = Math.floor(ms / 1000);
  const mins = Math.floor(totalSeconds / 60);
  const secs = totalSeconds % 60;
  const urgent = ms < 2 * 60 * 1000; // < 2 minutes
  const text =
    mins > 0
      ? `${mins}m ${secs.toString().padStart(2, "0")}s`
      : `${secs}s`;
  return { text, urgent };
}

export function CountdownTimer({ expiresAt, onExpired, className = "" }: CountdownTimerProps) {
  const expiry = useMemo(
    () => (typeof expiresAt === "string" ? new Date(expiresAt) : expiresAt),
    [expiresAt],
  );
  const [remaining, setRemaining] = useState(() => expiry.getTime() - Date.now());

  useEffect(() => {
    const tick = () => {
      const ms = expiry.getTime() - Date.now();
      setRemaining(ms);
      if (ms <= 0) onExpired?.();
    };

    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [expiry, onExpired]);

  const { text, urgent } = formatRemaining(remaining);

  return (
    <span
      aria-live="polite"
      aria-label={`Time remaining: ${text}`}
      className={[
        "inline-flex items-center gap-1 font-mono text-sm font-semibold tabular-nums",
        urgent ? "text-status-danger" : "text-chrome-700",
        className,
      ].join(" ")}
    >
      {urgent && <span aria-hidden="true">⏰</span>}
      {text}
    </span>
  );
}
