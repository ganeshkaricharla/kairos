export interface Habit {
  id: string;
  goal_id: string;
  user_id: string;
  title: string;
  description: string;
  frequency: string;
  time_of_day: string | null;
  duration_minutes: number | null;
  difficulty: string;
  reasoning: string;
  status: string;
  activated_at: string | null;
  replaced_by: string | null;
  replaces: string | null;
  order: number;
  linked_tracker_id: string | null;
  tracker_threshold: number | null;
  created_at: string;
  updated_at: string;
}
