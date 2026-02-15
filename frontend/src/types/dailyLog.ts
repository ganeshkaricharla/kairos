export interface HabitCompletion {
  habit_id: string;
  completed: boolean;
  completed_at: string | null;
  notes: string;
}

export interface TrackerEntry {
  tracker_id: string;
  value: number;
  logged_at: string | null;
  notes: string;
}

export interface DailyLog {
  id: string;
  user_id: string;
  goal_id: string;
  date: string;
  habit_completions: HabitCompletion[];
  tracker_entries: TrackerEntry[];
  created_at: string;
  updated_at: string;
}
