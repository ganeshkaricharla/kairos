import api from "./client";

export interface SystemSettings {
  session_lock_enabled: boolean;
  session_lock_hours: number;
  admin_emails: string;
}

export interface UpdateSettingsRequest {
  session_lock_enabled?: boolean;
  session_lock_hours?: number;
}

export interface SystemStats {
  total_users: number;
  total_goals: number;
  total_habits: number;
  total_sessions: number;
  active_sessions: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

export const adminApi = {
  getSettings: () =>
    api.get<SystemSettings>("/admin/settings").then((r) => r.data),

  updateSettings: (data: UpdateSettingsRequest) =>
    api.patch<SystemSettings>("/admin/settings", data).then((r) => r.data),

  getStats: () =>
    api.get<SystemStats>("/admin/stats").then((r) => r.data),

  getUsers: (limit = 50, skip = 0) =>
    api
      .get<{ users: User[]; total: number; limit: number; skip: number }>(
        `/admin/users?limit=${limit}&skip=${skip}`
      )
      .then((r) => r.data),
};
