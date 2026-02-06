export type TaskStatus = "pending" | "completed" | "postponed";

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  estimatedHours: number; // max 2h per micro-task
  weekNumber: number; // 1-4
  dayOfWeek: number; // 1-7
  order: number;
  createdAt: string;
  completedAt?: string;
  postponedAt?: string;
}

export interface WeekPlan {
  weekNumber: number;
  label: string;
  tasks: Task[];
}

export interface ProgressData {
  totalTasks: number;
  completedTasks: number;
  postponedTasks: number;
  pendingTasks: number;
  percentage: number;
}
