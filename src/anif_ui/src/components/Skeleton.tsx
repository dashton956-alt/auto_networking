interface SkeletonProps {
  className?: string;
  "aria-label"?: string;
}

export function Skeleton({ className = "", "aria-label": label = "Loading content" }: SkeletonProps) {
  return (
    <div
      aria-busy="true"
      aria-label={label}
      className={["animate-pulse rounded bg-chrome-200", className].join(" ")}
    />
  );
}

export function SkeletonText({ lines = 3 }: { lines?: number }) {
  return (
    <div className="space-y-2" aria-busy="true" aria-label="Loading text">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={["h-4", i === lines - 1 ? "w-3/4" : "w-full"].join(" ")}
        />
      ))}
    </div>
  );
}
