import api from "./client";
import type { Goal, GoalCreate } from "@/types/goal";

export const goalsApi = {
  getActive: () => api.get<Goal | null>("/goals").then((r) => r.data),

  get: (id: string) => api.get<Goal>(`/goals/${id}`).then((r) => r.data),

  create: (data: GoalCreate) =>
    api.post<Goal>("/goals", data).then((r) => r.data),

  update: (id: string, data: Partial<Goal>) =>
    api.patch<Goal>(`/goals/${id}`, data).then((r) => r.data),

  delete: (id: string) => api.delete(`/goals/${id}`).then((r) => r.data),
};
