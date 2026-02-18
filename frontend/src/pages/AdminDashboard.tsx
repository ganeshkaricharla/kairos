import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowLeft, Users, Settings, BarChart3, Lock, LockOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import { adminApi } from "@/api/admin";

export function AdminDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"settings" | "users" | "stats">("settings");

  // Redirect if not admin
  if (!user?.is_admin) {
    navigate("/");
    return null;
  }

  const { data: settings, isLoading: loadingSettings } = useQuery({
    queryKey: ["admin-settings"],
    queryFn: adminApi.getSettings,
  });

  const { data: stats } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: adminApi.getStats,
  });

  const { data: usersData } = useQuery({
    queryKey: ["admin-users"],
    queryFn: () => adminApi.getUsers(100, 0),
  });

  const updateSettings = useMutation({
    mutationFn: adminApi.updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-settings"] });
      toast.success("Settings updated successfully");
    },
    onError: (error: any) => {
      toast.error("Failed to update settings", {
        description: error?.response?.data?.detail || error.message,
      });
    },
  });

  const handleUpdateSettings = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    updateSettings.mutate({
      session_lock_enabled: formData.get("session_lock_enabled") === "true",
      session_lock_hours: Number(formData.get("session_lock_hours")),
    });
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate("/")}
          >
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Admin Dashboard</h1>
            <p className="text-sm text-muted-foreground">System configuration and monitoring</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab("settings")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "settings"
              ? "border-b-2 border-primary text-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Settings className="w-4 h-4 inline mr-2" />
          Settings
        </button>
        <button
          onClick={() => setActiveTab("stats")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "stats"
              ? "border-b-2 border-primary text-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <BarChart3 className="w-4 h-4 inline mr-2" />
          Statistics
        </button>
        <button
          onClick={() => setActiveTab("users")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "users"
              ? "border-b-2 border-primary text-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Users className="w-4 h-4 inline mr-2" />
          Users
        </button>
      </div>

      {/* Content */}
      {activeTab === "settings" && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">System Settings</h2>
          {loadingSettings ? (
            <p>Loading settings...</p>
          ) : (
            <form onSubmit={handleUpdateSettings} className="space-y-6">
              {/* Session Lock Settings */}
              <div className="space-y-4 border rounded-lg p-4">
                <h3 className="font-medium flex items-center gap-2">
                  {settings?.session_lock_enabled ? (
                    <Lock className="w-4 h-4" />
                  ) : (
                    <LockOpen className="w-4 h-4" />
                  )}
                  Coaching Session Lock
                </h3>

                <div className="space-y-2">
                  <Label htmlFor="session_lock_enabled">Enable Session Locking</Label>
                  <select
                    id="session_lock_enabled"
                    name="session_lock_enabled"
                    defaultValue={settings?.session_lock_enabled ? "true" : "false"}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value="true">Enabled</option>
                    <option value="false">Disabled</option>
                  </select>
                  <p className="text-sm text-muted-foreground">
                    Prevent users from opening new coaching sessions too soon after closing one
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="session_lock_hours">Lock Duration (hours)</Label>
                  <Input
                    id="session_lock_hours"
                    name="session_lock_hours"
                    type="number"
                    min="1"
                    max="168"
                    defaultValue={settings?.session_lock_hours || 6}
                    className="max-w-xs"
                  />
                  <p className="text-sm text-muted-foreground">
                    Number of hours to lock chat after resolving a session (1-168)
                  </p>
                </div>
              </div>

              {/* Admin Emails (Read-only) */}
              <div className="space-y-2">
                <Label>Admin Emails (configured in .env)</Label>
                <Input
                  value={settings?.admin_emails || "Not configured"}
                  disabled
                  className="bg-muted"
                />
                <p className="text-sm text-muted-foreground">
                  Update ADMIN_EMAILS in .env file to change admin users
                </p>
              </div>

              <div className="flex gap-2">
                <Button type="submit" disabled={updateSettings.isPending}>
                  {updateSettings.isPending ? "Saving..." : "Save Settings"}
                </Button>
                <p className="text-sm text-muted-foreground self-center">
                  Note: Changes are in-memory only. Update .env file for persistence.
                </p>
              </div>
            </form>
          )}
        </Card>
      )}

      {activeTab === "stats" && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Users</p>
                <p className="text-3xl font-bold">{stats?.total_users || 0}</p>
              </div>
              <Users className="w-8 h-8 text-muted-foreground" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Goals</p>
                <p className="text-3xl font-bold">{stats?.total_goals || 0}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-muted-foreground" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Habits</p>
                <p className="text-3xl font-bold">{stats?.total_habits || 0}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Sessions</p>
                <p className="text-3xl font-bold">{stats?.total_sessions || 0}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Sessions</p>
                <p className="text-3xl font-bold text-primary">
                  {stats?.active_sessions || 0}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === "users" && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">
            Users ({usersData?.total || 0})
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4">Name</th>
                  <th className="text-left py-2 px-4">Email</th>
                  <th className="text-left py-2 px-4">Admin</th>
                  <th className="text-left py-2 px-4">Created</th>
                </tr>
              </thead>
              <tbody>
                {usersData?.users.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-muted/50">
                    <td className="py-3 px-4 flex items-center gap-2">
                      {user.picture && (
                        <img
                          src={user.picture}
                          alt={user.name}
                          className="w-6 h-6 rounded-full"
                        />
                      )}
                      {user.name}
                    </td>
                    <td className="py-3 px-4">{user.email}</td>
                    <td className="py-3 px-4">
                      {user.is_admin ? (
                        <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded">
                          Admin
                        </span>
                      ) : (
                        <span className="text-xs bg-muted text-muted-foreground px-2 py-1 rounded">
                          User
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-sm text-muted-foreground">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
