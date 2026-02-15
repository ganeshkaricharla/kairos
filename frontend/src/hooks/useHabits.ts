import { useQuery } from "@tanstack/react-query";
import { habitsApi } from "@/api/habits";

export function useHabits(goalId: string, status?: string) {
  return useQuery({
    queryKey: ["habits", goalId, status],
    queryFn: () => habitsApi.list(goalId, status),
    enabled: !!goalId,
  });
}
