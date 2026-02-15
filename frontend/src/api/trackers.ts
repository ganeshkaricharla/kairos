import api from "./client";
import type { Tracker } from "@/types/tracker";

export const trackersApi = {
  list: (goalId: string) =>
    api.get<Tracker[]>(`/goals/${goalId}/trackers`).then((r) => r.data),

  update: (id: string, data: Partial<Tracker>) =>
    api.patch<Tracker>(`/trackers/${id}`, data).then((r) => r.data),
};
