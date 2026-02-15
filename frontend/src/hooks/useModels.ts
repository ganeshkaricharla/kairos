import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { modelsApi } from "@/api/models";

export function useModels(search?: string) {
  return useQuery({
    queryKey: ["models", search],
    queryFn: () => modelsApi.list(search),
  });
}

export function useSelectedModel() {
  return useQuery({
    queryKey: ["models", "selected"],
    queryFn: modelsApi.getSelected,
  });
}

export function useSelectModel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (modelId: string) => modelsApi.select(modelId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["models", "selected"] });
    },
  });
}
