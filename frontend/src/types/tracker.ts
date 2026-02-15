export interface Tracker {
  id: string;
  goal_id: string;
  user_id: string;
  name: string;
  description: string;
  unit: string;
  type: string;
  direction: string;
  target_value: number | null;
  current_value: number | null;
  reasoning: string;
  created_at: string;
  updated_at: string;
}
