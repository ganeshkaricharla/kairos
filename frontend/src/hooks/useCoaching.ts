import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { coachingApi } from "@/api/coaching";
import type { CoachingSession } from "@/types/coaching";

export function useActiveCoaching(goalId: string) {
  return useQuery({
    queryKey: ["coaching", goalId],
    queryFn: () => coachingApi.getActive(goalId),
    enabled: !!goalId,
  });
}

export function useStartCoaching() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      goalId,
      trigger,
    }: {
      goalId: string;
      trigger?: string;
    }) => coachingApi.start(goalId, trigger),
    onSuccess: (data, vars) => {
      qc.setQueryData(["coaching", vars.goalId], data);
    },
  });
}

export function useSendMessage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      message,
    }: {
      sessionId: string;
      message: string;
      goalId: string;
    }) => coachingApi.sendMessage(sessionId, message),

    onMutate: async ({ message, goalId }) => {
      await qc.cancelQueries({ queryKey: ["coaching", goalId] });
      const previous = qc.getQueryData<CoachingSession | null>([
        "coaching",
        goalId,
      ]);

      // Optimistically add the user message so it appears immediately
      if (previous) {
        qc.setQueryData<CoachingSession | null>(["coaching", goalId], {
          ...previous,
          messages: [
            ...previous.messages,
            {
              role: "user",
              content: message,
              timestamp: new Date().toISOString(),
            },
          ],
        });
      }

      return { previous };
    },

    onSuccess: (data, vars) => {
      // Replace with the full server response (includes AI reply)
      qc.setQueryData(["coaching", vars.goalId], data);
    },

    onError: (_err, vars, context) => {
      if (context?.previous) {
        qc.setQueryData(["coaching", vars.goalId], context.previous);
      }
    },
  });
}

export function useAcceptChange() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      index,
    }: {
      sessionId: string;
      index: number;
      goalId: string;
    }) => coachingApi.acceptChange(sessionId, index),
    onSuccess: (data, vars) => {
      qc.setQueryData(["coaching", vars.goalId], data);
      qc.invalidateQueries({ queryKey: ["activeGoal"] });
    },
  });
}

export function useRejectChange() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      index,
    }: {
      sessionId: string;
      index: number;
      goalId: string;
    }) => coachingApi.rejectChange(sessionId, index),
    onSuccess: (data, vars) => {
      qc.setQueryData(["coaching", vars.goalId], data);
    },
  });
}

export function useResolveSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
    }: {
      sessionId: string;
      goalId: string;
    }) => coachingApi.resolve(sessionId),
    onSuccess: (data, vars) => {
      qc.setQueryData(["coaching", vars.goalId], data);
    },
  });
}
