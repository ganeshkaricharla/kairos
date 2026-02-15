import api from "./client";
import type { DailyLog } from "@/types/dailyLog";

export const dailyLogsApi = {
  get: (date: string) =>
    api.get<DailyLog[]>(`/daily/${date}`).then((r) => r.data),

  toggleHabit: (date: string, goalId: string, habitId: string) =>
    api
      .post<DailyLog>(
        `/daily/${date}/goals/${goalId}/habits/${habitId}/toggle`
      )
      .then((r) => r.data),

  logTracker: (
    date: string,
    goalId: string,
    trackerId: string,
    value: number,
    notes: string = ""
  ) =>
    api
      .post<DailyLog>(
        `/daily/${date}/goals/${goalId}/trackers/${trackerId}/log`,
        { value, notes }
      )
      .then((r) => r.data),
};
