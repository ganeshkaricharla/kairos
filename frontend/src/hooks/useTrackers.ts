import { useQuery } from "@tanstack/react-query";
import { trackersApi } from "@/api/trackers";

export function useTrackers(goalId: string) {
  return useQuery({
    queryKey: ["trackers", goalId],
    queryFn: () => trackersApi.list(goalId),
    enabled: !!goalId,
  });
}
