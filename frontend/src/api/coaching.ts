import api from "./client";
import type { CoachingSession } from "@/types/coaching";

export const coachingApi = {
  getActive: (goalId: string) =>
    api
      .get<CoachingSession | null>(`/goals/${goalId}/coaching`)
      .then((r) => r.data),

  start: (goalId: string, trigger: string = "scheduled_review") =>
    api
      .post<CoachingSession>(
        `/goals/${goalId}/coaching/start?trigger=${trigger}`
      )
      .then((r) => r.data),

  sendMessage: (sessionId: string, message: string) =>
    api
      .post<CoachingSession>(`/coaching/${sessionId}/message`, { message })
      .then((r) => r.data),

  acceptChange: (sessionId: string, index: number) =>
    api
      .post<CoachingSession>(`/coaching/${sessionId}/accept-change/${index}`)
      .then((r) => r.data),

  rejectChange: (sessionId: string, index: number) =>
    api
      .post<CoachingSession>(`/coaching/${sessionId}/reject-change/${index}`)
      .then((r) => r.data),

  resolve: (sessionId: string) =>
    api
      .post<CoachingSession>(`/coaching/${sessionId}/resolve`)
      .then((r) => r.data),
};
