"use client";

import { ProgressData } from "@/types/task";
import { ProgressBar } from "@/components/ui/progress-bar";
import { Card } from "@/components/ui/card";
import { Target, CheckCircle2, Clock, AlertCircle } from "lucide-react";

interface ProgressOverviewProps {
  total: ProgressData;
  currentWeek: ProgressData;
  weekNumber: number;
}

export function ProgressOverview({
  total,
  currentWeek,
  weekNumber,
}: ProgressOverviewProps) {
  return (
    <Card>
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-stone-800">Tu Progreso</h2>
        <p className="text-sm text-stone-400">
          Semana {weekNumber} de 4 &middot; Sigue así, paso a paso.
        </p>
      </div>

      <div className="space-y-5">
        <ProgressBar
          value={total.percentage}
          label="Progreso Total"
          sublabel={`${total.completedTasks} de ${total.totalTasks}`}
          size="lg"
          variant={total.percentage >= 75 ? "success" : "default"}
        />

        <ProgressBar
          value={currentWeek.percentage}
          label={`Semana ${weekNumber}`}
          sublabel={`${currentWeek.completedTasks} de ${currentWeek.totalTasks}`}
          size="md"
          variant={
            currentWeek.percentage === 100
              ? "success"
              : currentWeek.postponedTasks > 0
              ? "warning"
              : "default"
          }
        />
      </div>

      <div className="mt-6 grid grid-cols-4 gap-3">
        <StatCard
          icon={Target}
          label="Total"
          value={total.totalTasks}
          color="text-stone-600"
        />
        <StatCard
          icon={CheckCircle2}
          label="Hechas"
          value={total.completedTasks}
          color="text-emerald-600"
        />
        <StatCard
          icon={Clock}
          label="Pendientes"
          value={total.pendingTasks}
          color="text-stone-400"
        />
        <StatCard
          icon={AlertCircle}
          label="Postergadas"
          value={total.postponedTasks}
          color="text-amber-500"
        />
      </div>
    </Card>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ElementType;
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className="flex flex-col items-center gap-1 rounded-xl bg-stone-50 p-3">
      <Icon className={`h-4 w-4 ${color}`} />
      <span className="text-lg font-bold tabular-nums text-stone-800">
        {value}
      </span>
      <span className="text-xs text-stone-400">{label}</span>
    </div>
  );
}
