import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { goalsApi } from "@/api/goals";
import type { GoalCreate } from "@/types/goal";

export function useGoal(id?: string) {
  return useQuery({
    queryKey: ["goal", id],
    queryFn: () => goalsApi.get(id!),
    enabled: !!id,
  });
}

export function useActiveGoal() {
  return useQuery({
    queryKey: ["activeGoal"],
    queryFn: goalsApi.getActive,
  });
}

export function useCreateGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: GoalCreate) => goalsApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["activeGoal"] }),
  });
}

export function useDeleteGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => goalsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["activeGoal"] }),
  });
}
