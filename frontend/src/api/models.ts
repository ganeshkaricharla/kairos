import api from "./client";

export interface AIModel {
  id: string;
  name: string;
  context_length: number | null;
  pricing: {
    prompt?: string;
    completion?: string;
  };
}

export interface SelectedModel {
  model_id: string | null;
}

export const modelsApi = {
  list: (search?: string) =>
    api
      .get<AIModel[]>("/models", { params: search ? { search } : undefined })
      .then((r) => r.data),

  getSelected: () =>
    api.get<SelectedModel>("/models/selected").then((r) => r.data),

  select: (model_id: string) =>
    api.post("/models/select", { model_id }).then((r) => r.data),
};
