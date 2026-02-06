import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "pending" | "completed" | "postponed";
  className?: string;
}

const variantStyles = {
  pending:
    "bg-stone-100 text-stone-600 border-stone-200",
  completed:
    "bg-emerald-50 text-emerald-700 border-emerald-200",
  postponed:
    "bg-amber-50 text-amber-700 border-amber-200",
};

export function Badge({ children, variant = "pending", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
