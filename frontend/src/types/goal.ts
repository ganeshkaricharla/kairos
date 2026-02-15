export interface AIContext {
  summary: string;
  plan_philosophy: string;
  current_phase: string;
  next_review_date: string | null;
}

export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description: string;
  target_date: string | null;
  status: string;
  ai_context: AIContext;
  habits?: Habit[];
  trackers?: Tracker[];
  created_at: string;
  updated_at: string;
}

export interface GoalCreate {
  title: string;
  description: string;
  target_date?: string;
}

// Re-export for convenience
import type { Habit } from "./habit";
import type { Tracker } from "./tracker";
