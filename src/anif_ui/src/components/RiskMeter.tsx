/** Visual 0–100 risk score indicator — used throughout approval queue and audit (ANIF-304). */

interface RiskMeterProps {
  score: number;
  showLabel?: boolean;
  className?: string;
}

function riskBand(score: number): { label: string; bar: string; text: string } {
  if (score <= 30) return { label: "Low", bar: "bg-risk-low", text: "text-risk-low" };
  if (score <= 69) return { label: "Medium", bar: "bg-risk-medium", text: "text-risk-medium" };
  return { label: "High", bar: "bg-risk-high", text: "text-risk-high" };
}

export function RiskMeter({ score, showLabel = true, className = "" }: RiskMeterProps) {
  const pct = Math.max(0, Math.min(100, score));
  const band = riskBand(pct);

  return (
    <div className={["flex items-center gap-2", className].join(" ")}>
      <div
        role="meter"
        aria-label={`Risk score: ${pct} out of 100 — ${band.label}`}
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        className="flex-1 h-2 rounded-full bg-chrome-200 overflow-hidden min-w-[80px]"
      >
        <div
          className={["h-full rounded-full transition-all", band.bar].join(" ")}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showLabel && (
        <span className={["text-sm font-semibold tabular-nums min-w-[2rem] text-right", band.text].join(" ")}>
          {pct}
        </span>
      )}
    </div>
  );
}

export function RiskBadge({ score }: { score: number }) {
  const pct = Math.max(0, Math.min(100, score));
  const band = riskBand(pct);
  return (
    <span className={["inline-flex items-center gap-1 text-xs font-semibold", band.text].join(" ")}>
      <span aria-hidden="true">●</span>
      {band.label} ({pct})
    </span>
  );
}
