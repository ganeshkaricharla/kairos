import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { dailyLogsApi } from "@/api/dailyLogs";
import type { DailyLog } from "@/types/dailyLog";
import { format } from "date-fns";

export function useToday() {
  const date = format(new Date(), "yyyy-MM-dd");

  return useQuery({
    queryKey: ["daily", date],
    queryFn: () => dailyLogsApi.get(date),
  });
}

export function useToggleHabit() {
  const qc = useQueryClient();
  const date = format(new Date(), "yyyy-MM-dd");

  return useMutation({
    mutationFn: ({
      goalId,
      habitId,
    }: {
      goalId: string;
      habitId: string;
    }) => dailyLogsApi.toggleHabit(date, goalId, habitId),

    onMutate: async ({ goalId, habitId }) => {
      await qc.cancelQueries({ queryKey: ["daily", date] });
      const previous = qc.getQueryData<DailyLog[]>(["daily", date]);

      qc.setQueryData<DailyLog[]>(["daily", date], (old) => {
        if (!old) {
          // No log yet — create an optimistic one
          return [
            {
              id: "optimistic",
              user_id: "default",
              goal_id: goalId,
              date,
              habit_completions: [
                {
                  habit_id: habitId,
                  completed: true,
                  completed_at: new Date().toISOString(),
                  notes: "",
                },
              ],
              tracker_entries: [],
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
          ];
        }

        return old.map((log) => {
          if (log.goal_id !== goalId) return log;

          const existing = log.habit_completions.find(
            (c) => c.habit_id === habitId
          );
          const updatedCompletions = existing
            ? log.habit_completions.map((c) =>
                c.habit_id === habitId
                  ? { ...c, completed: !c.completed }
                  : c
              )
            : [
                ...log.habit_completions,
                {
                  habit_id: habitId,
                  completed: true,
                  completed_at: new Date().toISOString(),
                  notes: "",
                },
              ];

          return { ...log, habit_completions: updatedCompletions };
        });
      });

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        qc.setQueryData(["daily", date], context.previous);
      }
    },

    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["daily", date] });
    },
  });
}

export function useLogTracker() {
  const qc = useQueryClient();
  const date = format(new Date(), "yyyy-MM-dd");

  return useMutation({
    mutationFn: ({
      goalId,
      trackerId,
      value,
    }: {
      goalId: string;
      trackerId: string;
      value: number;
    }) => dailyLogsApi.logTracker(date, goalId, trackerId, value),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["daily", date] });
    },
  });
}
