"use client";

import { Task, TaskStatus } from "@/types/task";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Check, Clock, CircleDashed } from "lucide-react";

interface TaskItemProps {
  task: Task;
  onStatusChange: (taskId: string, newStatus: TaskStatus) => void;
}

const statusConfig = {
  pending: {
    icon: CircleDashed,
    label: "Pendiente",
    badgeVariant: "pending" as const,
    iconColor: "text-stone-400",
  },
  completed: {
    icon: Check,
    label: "Completada",
    badgeVariant: "completed" as const,
    iconColor: "text-emerald-600",
  },
  postponed: {
    icon: Clock,
    label: "Postergada",
    badgeVariant: "postponed" as const,
    iconColor: "text-amber-500",
  },
};

export function TaskItem({ task, onStatusChange }: TaskItemProps) {
  const config = statusConfig[task.status];

  const cycleStatus = () => {
    const next: Record<TaskStatus, TaskStatus> = {
      pending: "completed",
      completed: "postponed",
      postponed: "pending",
    };
    onStatusChange(task.id, next[task.status]);
  };

  return (
    <div
      className={cn(
        "group flex items-start gap-3 rounded-xl border border-transparent p-3 transition-all duration-200",
        "hover:border-stone-200 hover:bg-stone-50/50",
        task.status === "completed" && "opacity-60"
      )}
    >
      <button
        onClick={cycleStatus}
        className={cn(
          "mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 transition-colors",
          task.status === "completed"
            ? "border-emerald-600 bg-emerald-600 text-white"
            : task.status === "postponed"
            ? "border-amber-400 bg-amber-50"
            : "border-stone-300 hover:border-stone-400"
        )}
        aria-label={`Cambiar estado de: ${task.title}`}
      >
        {task.status === "completed" && <Check className="h-3.5 w-3.5" />}
        {task.status === "postponed" && (
          <Clock className="h-3 w-3 text-amber-500" />
        )}
      </button>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p
            className={cn(
              "text-sm font-medium text-stone-800",
              task.status === "completed" && "line-through text-stone-400"
            )}
          >
            {task.title}
          </p>
        </div>
        {task.description && (
          <p className="mt-0.5 text-xs text-stone-400 line-clamp-1">
            {task.description}
          </p>
        )}
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <span className="text-xs text-stone-300 tabular-nums">
          {task.estimatedHours}h
        </span>
        <Badge variant={config.badgeVariant}>{config.label}</Badge>
      </div>
    </div>
  );
}
