import api from "./client";
import type { Habit } from "@/types/habit";

export const habitsApi = {
  list: (goalId: string, status?: string) =>
    api
      .get<Habit[]>(`/goals/${goalId}/habits`, {
        params: status ? { status } : undefined,
      })
      .then((r) => r.data),

  update: (id: string, data: Partial<Habit>) =>
    api.patch<Habit>(`/habits/${id}`, data).then((r) => r.data),
};
