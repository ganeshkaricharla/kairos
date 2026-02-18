export interface ToolCall {
  name: string;
  description: string;
  arguments?: Record<string, unknown>;
}

export interface ChatMessage {
  role: "assistant" | "user";
  content: string;
  timestamp: string;
  tool_calls?: ToolCall[];  // Tool calls made by AI (for UI display)
}

export interface ProposedChange {
  type: string;
  description: string;
  details: Record<string, unknown>;
  accepted: boolean | null;
}

export interface HabitPerformance {
  habit_id: string;
  title: string;
  completed_count: number;
  total_days: number;
  rate: number;
}

export interface TrackerTrend {
  tracker_id: string;
  name: string;
  values: number[];
  trend: string;
}

export interface PerformanceSnapshot {
  period_start: string;
  period_end: string;
  habits: HabitPerformance[];
  tracker_trends: TrackerTrend[];
}

export interface SessionSummary {
  key_points: string[];
  habits_added: string[];
  next_check_in: string | null;
  action_items: string[];
}

export interface CoachingSession {
  id: string;
  goal_id: string;
  user_id: string;
  trigger: string;
  status: string;
  performance_snapshot: PerformanceSnapshot | null;
  messages: ChatMessage[];
  proposed_changes: ProposedChange[];
  summary: SessionSummary | null;
  created_at: string;
  resolved_at: string | null;
}
