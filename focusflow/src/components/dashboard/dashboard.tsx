"use client";

import { useState } from "react";
import { Task, TaskStatus } from "@/types/task";
import { mockTasks, getWeekPlans, calculateProgress } from "@/lib/mock-data";
import { ProgressOverview } from "./progress-overview";
import { WeekSection } from "./week-section";
import { Brain } from "lucide-react";

const CURRENT_WEEK = 2;

export function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>(mockTasks);

  const handleStatusChange = (taskId: string, newStatus: TaskStatus) => {
    setTasks((prev) =>
      prev.map((t) =>
        t.id === taskId
          ? {
              ...t,
              status: newStatus,
              completedAt:
                newStatus === "completed"
                  ? new Date().toISOString()
                  : undefined,
              postponedAt:
                newStatus === "postponed"
                  ? new Date().toISOString()
                  : undefined,
            }
          : t
      )
    );
  };

  const weekPlans = getWeekPlans(tasks);
  const totalProgress = calculateProgress(tasks);
  const currentWeekTasks = tasks.filter((t) => t.weekNumber === CURRENT_WEEK);
  const currentWeekProgress = calculateProgress(currentWeekTasks);

  return (
    <div className="min-h-screen bg-stone-50/50">
      {/* Header */}
      <header className="border-b border-stone-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-stone-800">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-stone-800">
                FocusFlow
              </h1>
              <p className="text-xs text-stone-400">
                De ideas a acción, paso a paso
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-stone-200" />
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-3xl px-6 py-8">
        <div className="space-y-6">
          {/* Greeting */}
          <div>
            <h2 className="text-2xl font-semibold text-stone-800">
              Buen día 👋
            </h2>
            <p className="mt-1 text-sm text-stone-400">
              Tu plan de 4 semanas está en marcha. Cada micro-tarea te acerca a
              tu meta.
            </p>
          </div>

          {/* Progress Overview */}
          <ProgressOverview
            total={totalProgress}
            currentWeek={currentWeekProgress}
            weekNumber={CURRENT_WEEK}
          />

          {/* Weekly Sections */}
          <div className="space-y-4">
            {weekPlans.map((week) => (
              <WeekSection
                key={week.weekNumber}
                week={week}
                isCurrentWeek={week.weekNumber === CURRENT_WEEK}
                onTaskStatusChange={handleStatusChange}
              />
            ))}
          </div>

          {/* Footer hint */}
          <p className="pb-8 text-center text-xs text-stone-300">
            Las tareas postergadas se recalculan automáticamente al inicio del
            siguiente periodo.
          </p>
        </div>
      </main>
    </div>
  );
}
