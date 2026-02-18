export interface AIContext {
  summary: string;
  plan_philosophy: string;
  current_phase: string;
  next_review_date: string | null;
}

export interface Goal {
  id: string;
  user_id: string;
  template_id: string;
  title: string;
  description: string;
  primary_metric_name: string;
  primary_metric_unit: string;
  initial_value?: number;  // Starting value for primary metric
  target_value?: number;   // Target value for primary metric
  target_date: string | null;
  status: string;
  ai_context: AIContext;
  habits?: Habit[];
  trackers?: Tracker[];
  created_at: string;
  updated_at: string;
}

export interface GoalCreate {
  template_id: string;
  description: string;
  initial_value?: number;  // Starting value for primary metric
  target_value?: number;   // Target value for primary metric
  target_date?: string;
  questionnaire_responses?: Record<string, string>;  // question_id -> selected answer value
}

// Re-export for convenience
import type { Habit } from "./habit";
import type { Tracker } from "./tracker";
