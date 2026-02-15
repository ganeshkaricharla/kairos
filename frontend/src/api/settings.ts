import api from "./client";

export interface AIConfig {
  provider: string | null;
  api_key_masked: string | null;
  base_url: string | null;
  organization_id: string | null;
  using_global_key: boolean;
}

export interface AIConfigUpdate {
  provider: string;
  api_key: string;
  base_url?: string;
  organization_id?: string;
}

export interface AITestResult {
  success: boolean;
  message: string;
  error: string | null;
}

export const settingsApi = {
  getAIConfig: () =>
    api.get<AIConfig>("/users/me/ai-config").then((r) => r.data),

  updateAIConfig: (data: AIConfigUpdate) =>
    api.patch("/users/me/ai-config", data).then((r) => r.data),

  deleteAIConfig: () =>
    api.delete("/users/me/ai-config").then((r) => r.data),

  testAIConfig: (data: { provider: string; api_key: string; base_url?: string }) =>
    api.post<AITestResult>("/users/me/ai-config/test", data).then((r) => r.data),
};
