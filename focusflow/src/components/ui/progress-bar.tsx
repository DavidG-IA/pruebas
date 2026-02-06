"use client";

import { cn } from "@/lib/utils";

interface ProgressBarProps {
  value: number; // 0-100
  label: string;
  sublabel?: string;
  size?: "sm" | "md" | "lg";
  variant?: "default" | "success" | "warning";
  showPercentage?: boolean;
  className?: string;
}

const sizeStyles = {
  sm: "h-1.5",
  md: "h-2.5",
  lg: "h-4",
};

const variantStyles = {
  default: "bg-stone-700",
  success: "bg-emerald-600",
  warning: "bg-amber-500",
};

const variantTrackStyles = {
  default: "bg-stone-200",
  success: "bg-emerald-100",
  warning: "bg-amber-100",
};

export function ProgressBar({
  value,
  label,
  sublabel,
  size = "md",
  variant = "default",
  showPercentage = true,
  className,
}: ProgressBarProps) {
  const clampedValue = Math.min(100, Math.max(0, value));

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-baseline justify-between">
        <span className="text-sm font-medium text-stone-700">{label}</span>
        <div className="flex items-baseline gap-1.5">
          {sublabel && (
            <span className="text-xs text-stone-400">{sublabel}</span>
          )}
          {showPercentage && (
            <span className="text-sm font-semibold tabular-nums text-stone-800">
              {clampedValue}%
            </span>
          )}
        </div>
      </div>
      <div
        className={cn(
          "w-full overflow-hidden rounded-full",
          variantTrackStyles[variant],
          sizeStyles[size]
        )}
      >
        <div
          className={cn(
            "h-full rounded-full transition-all duration-700 ease-out",
            variantStyles[variant]
          )}
          style={{ width: `${clampedValue}%` }}
          role="progressbar"
          aria-valuenow={clampedValue}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={label}
        />
      </div>
    </div>
  );
}
