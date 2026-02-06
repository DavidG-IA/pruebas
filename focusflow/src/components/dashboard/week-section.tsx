"use client";

import { WeekPlan, TaskStatus } from "@/types/task";
import { TaskItem } from "./task-item";
import { ProgressBar } from "@/components/ui/progress-bar";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { calculateProgress } from "@/lib/mock-data";

interface WeekSectionProps {
  week: WeekPlan;
  isCurrentWeek?: boolean;
  onTaskStatusChange: (taskId: string, newStatus: TaskStatus) => void;
}

export function WeekSection({
  week,
  isCurrentWeek = false,
  onTaskStatusChange,
}: WeekSectionProps) {
  const progress = calculateProgress(week.tasks);

  return (
    <Card className={isCurrentWeek ? "ring-2 ring-stone-300 ring-offset-2" : ""}>
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-3">
          <CardTitle>{week.label}</CardTitle>
          {isCurrentWeek && (
            <span className="rounded-full bg-stone-800 px-2.5 py-0.5 text-xs font-medium text-white">
              Actual
            </span>
          )}
        </div>
        <span className="text-xs text-stone-400">
          {progress.completedTasks}/{progress.totalTasks} tareas
        </span>
      </CardHeader>

      <ProgressBar
        value={progress.percentage}
        label="Progreso semanal"
        sublabel={`${progress.completedTasks} completadas`}
        size="sm"
        variant={progress.percentage === 100 ? "success" : "default"}
        className="mb-4"
      />

      <div className="space-y-1">
        {week.tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onStatusChange={onTaskStatusChange}
          />
        ))}
        {week.tasks.length === 0 && (
          <p className="py-4 text-center text-sm text-stone-300">
            Sin tareas asignadas
          </p>
        )}
      </div>
    </Card>
  );
}
