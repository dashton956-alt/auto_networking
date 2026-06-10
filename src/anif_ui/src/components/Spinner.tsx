type Size = "sm" | "md" | "lg";

interface SpinnerProps {
  size?: Size;
  className?: string;
  "aria-label"?: string;
}

const sizeClasses: Record<Size, string> = {
  sm: "h-4 w-4 border-2",
  md: "h-6 w-6 border-2",
  lg: "h-8 w-8 border-[3px]",
};

export function Spinner({ size = "md", className = "", "aria-label": label = "Loading" }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-label={label}
      className={[
        "inline-block rounded-full border-current border-r-transparent animate-spin",
        sizeClasses[size],
        className,
      ].join(" ")}
    />
  );
}
